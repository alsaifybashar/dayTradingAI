"""
Quantitative Engine
------------------
Implements advanced mathematical models for the Elite Trading Paradigm.

Includes:
1. Microstructure: Order Book Imbalance (OBI), VPIN (Simulated)
2. Stat Arb: Ornstein-Uhlenbeck (OU) Mean Reversion
3. Risk: Kelly Criterion, VaR (Value at Risk)
4. Portfolio: Black-Litterman View Construction
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
import math
from typing import List, Dict, Tuple

class QuantEngine:
    def __init__(self):
        self.risk_free_rate = 0.04  # 4% annual
        
    # ==========================================
    # 2. Market Microstructure
    # ==========================================
    
    def calculate_obi(self, bids: List[Dict], asks: List[Dict], depth_weighted: bool = True) -> float:
        """
        Calculates Order Book Imbalance (OBI).
        
        Args:
            bids: List of {'price': float, 'size': float}
            asks: List of {'price': float, 'size': float}
            depth_weighted: If True, uses decay function for deeper levels.
            
        Returns:
            float: Imbalance [-1, 1] (Positive = Buy Pressure)
        """
        if not bids or not asks:
            return 0.0
            
        if not depth_weighted:
            # Level 1 Imbalance
            best_bid_vol = bids[0]['size']
            best_ask_vol = asks[0]['size']
            return (best_bid_vol - best_ask_vol) / (best_bid_vol + best_ask_vol)
        
        # Depth-Weighted Imbalance (Lambda decay)
        # formula: w_i = e^(-lambda * (i-1))
        # decay_lambda = 0.5 for generic usage
        decay_lambda = 0.5
        
        sum_bid_weighted = 0.0
        sum_ask_weighted = 0.0
        
        # Process up to 5 levels
        for i in range(min(len(bids), 5)):
            weight = math.exp(-decay_lambda * i)
            sum_bid_weighted += bids[i]['size'] * weight
            
        for i in range(min(len(asks), 5)):
            weight = math.exp(-decay_lambda * i)
            sum_ask_weighted += asks[i]['size'] * weight
            
        total_volume = sum_bid_weighted + sum_ask_weighted
        if total_volume == 0:
            return 0.0
            
        return (sum_bid_weighted - sum_ask_weighted) / total_volume

    def calculate_vpin_proxy(self, buys: int, sells: int, total_volume: int) -> float:
        """
        Simplified VPIN (Volume-Synchronized Probability of Informed Trading) proxy.
        In a real system, this uses volume buckets. Here we use flow imbalance.
        
        OFI = |Buys - Sells|
        VPIN ~ Rolling(OFI) / Volume
        """
        if total_volume == 0:
            return 0.0
        return abs(buys - sells) / total_volume

    # ==========================================
    # 3. Statistical Arbitrage (Mean Reversion)
    # ==========================================

    def estimate_ou_parameters(self, price_series: List[float]) -> Dict:
        """
        Estimates Ornstein-Uhlenbeck process parameters for a price series.
        dx_t = theta * (mu - x_t) * dt + sigma * dW_t
        
        Discrete AR(1): x_{t+1} = a + b * x_t + epsilon
        theta = -ln(b) / dt
        mu = a / (1 - b)
        sigma = std(epsilon) * sqrt(-2*ln(b) / (1-b^2) / dt)
        """
        if len(price_series) < 30:
            return {"z_score": 0, "action": "WAIT"}
            
        # Convert to numpy
        prices = np.array(price_series)
        x_t = prices[:-1]
        x_t1 = prices[1:]
        
        # Linear Regression: x_{t+1} = alpha + beta * x_t
        # Using numpy polyfit
        beta, alpha = np.polyfit(x_t, x_t1, 1)
        
        epsilon = x_t1 - (alpha + beta * x_t)
        sigma_epsilon = np.std(epsilon)
        
        # Calculate OU params
        dt = 1 # Assuming unit time step for simplicity
        
        # Avoid math errors if beta >= 1 (non-mean reverting)
        if beta >= 0.999: 
            return {"z_score": 0, "mean_reverting": False}
        
        theta = -np.log(beta) / dt
        mu = alpha / (1 - beta)
        sigma = sigma_epsilon * np.sqrt(-2 * np.log(beta) / (1 - beta**2) / dt)
        sigma_eq = sigma / np.sqrt(2 * theta)
        
        # Calculate current Z-Score
        current_price = price_series[-1]
        z_score = (current_price - mu) / sigma_eq
        
        return {
            "theta": theta,
            "mu": mu,
            "sigma": sigma,
            "z_score": z_score,
            "mean_reverting": True
        }

    # ==========================================
    # 5. Black-Litterman Logic (Simplified)
    # ==========================================
    
    def calculate_bl_view_return(self, sentiment_score: float, current_volatility: float) -> float:
        """
        Maps AI sentiment score [-100, 100] to an expected excess return (Q)
        Logic: Q_k = alpha * S_k * sigma_k
        alpha: confidence/aggressiveness factor
        """
        # Normalize sentiment to [-1, 1]
        s_k = sentiment_score / 100.0
        
        # Aggressiveness factor (elite default: 1.5 standard deviations for max sentiment)
        alpha = 1.5  
        
        q_k = alpha * s_k * current_volatility
        return q_k

    # ==========================================
    # 8. Risk Management
    # ==========================================

    def calculate_kelly_criterion(self, win_rate: float, win_loss_ratio: float, 
                                  half_kelly: bool = True) -> float:
        """
        Calculates optimal position size fraction using Kelly Criterion.
        f* = (p(b+1) - 1) / b
        where:
        p = win probability
        b = win/loss ratio (avg_win / avg_loss)
        """
        if win_loss_ratio <= 0:
            return 0.0
            
        f_star = (win_rate * (win_loss_ratio + 1) - 1) / win_loss_ratio
        
        if f_star <= 0:
            return 0.0
            
        if half_kelly:
            return f_star / 2
            
        return f_star

    def calculate_var(self, portfolio_value: float, returns: List[float], 
                      confidence_level: float = 0.95) -> Dict:
        """
        Calculates Value at Risk using Parametric method.
        """
        if not returns or len(returns) < 2:
            return {"var_95": 0, "var_percent": 0}
            
        mu = np.mean(returns)
        sigma = np.std(returns)
        
        # Z-score for confidence (e.g., 1.645 for 95%)
        z_score = norm.ppf(confidence_level)
        
        # VaR = -(mu - z * sigma) * PortfolioValue
        # We assume daily VaR
        var_pct = -(mu - z_score * sigma)
        var_value = var_pct * portfolio_value
        
        return {
            "var_value": max(0, var_value), # Value at risk (positive number)
            "var_percent": max(0, var_pct * 100)
        }

    def almgren_chriss_trajectory(self, total_shares: int, minutes: int = 15) -> List[int]:
        """
        Simplified Almgren-Chriss implementation for execution schedule.
        Returns share counts per minute block to minimize impact.
        Uses Hyperbolic Cosine trajectory.
        """
        # Hardcoded risk aversion and liquidity params for simulation
        risk_aversion = 1e-6 
        volatility = 0.02
        liquidity_coeff = 2e-7
        
        T = minutes
        zeta = math.sqrt((risk_aversion * volatility**2) / liquidity_coeff)
        
        schedule = []
        shares_remaining = total_shares
        
        # If zeta too small, linear schedule (TWAP)
        if zeta < 1e-4:
            per_min = int(total_shares / minutes)
            return [per_min] * minutes
            
        # Calculate v(t) trajectory
        try:
            sinh_zeta_T = math.sinh(zeta * T)
            for t in range(T):
                # Rate at time t
                # v(t) = (zeta * X / sinh(zeta*T)) * cosh(zeta*(T-t))
                rate = (zeta * total_shares / sinh_zeta_T) * math.cosh(zeta * (T - t))
                shares = int(rate) # Discrete shares
                if shares > shares_remaining: shares = shares_remaining
                schedule.append(shares)
                shares_remaining -= shares
                
            # Distribute remainder
            if shares_remaining > 0:
                schedule[-1] += shares_remaining
                
            return schedule
        except:
            # Fallback to TWAP
            return [int(total_shares/minutes)] * minutes

quant_engine = QuantEngine()
