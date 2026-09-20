class Household:
    """
    Represents a household's financial and cognitive state at time t.
    """
    def __init__(self, 
                 initial_balance: float, 
                 debt: float, 
                 obligations: float, 
                 base_income: float,
                 attention_sensitivity: float = 0.5):
        
        # State Vector S_t
        self.balance = initial_balance       # B_t
        self.debt = debt                     # D_t
        self.obligations = obligations       # O_t
        self.income = base_income            # Y_t
        self.attention = 1.0                 # A_t (Starts at 100% capacity)
        self.information_set = []            # I_t
        
        # Model Parameters
        self.alpha = attention_sensitivity   # Sensitivity of attention to financial stress
        
        # Tracking history for the final research data
        self.history = []

    def calculate_debt_service(self) -> float:
        """Calculates minimum required debt payment for the period."""
        # Simplified: assume 5% minimum payment on outstanding debt
        return self.debt * 0.05 if self.debt > 0 else 0.0

    def update_attention(self):
        """
        Updates attention capacity A_{t+1} based on financial stress.
        Formula: A_{t+1} = 1 - alpha * ((O_t + DebtService) / (B_t + Y_{t+1}))
        """
        available_resources = self.balance + self.income
        if available_resources <= 0:
            self.attention = 0.1 # Floor attention to prevent negative values
            return

        fixed_costs = self.obligations + self.calculate_debt_service()
        stress_ratio = fixed_costs / available_resources
        
        # Calculate new attention, bound between 0.1 and 1.0
        new_attention = 1.0 - (self.alpha * stress_ratio)
        self.attention = max(0.1, min(1.0, new_attention))

    def step(self, chosen_action_cost: float, income_shock: float = 0.0):
        """
        Advances the household state from t to t+1.
        """
        # 1. Realize income with potential stochastic shock
        current_income = self.income + income_shock
        
        # 2. Update liquid balance B_{t+1}
        self.balance = (self.balance 
                        + current_income 
                        - self.obligations 
                        - self.calculate_debt_service() 
                        - chosen_action_cost)
        
        # 3. Update cognitive bandwidth based on new financial state
        self.update_attention()
        
        # 4. Record state for empirical analysis
        self.record_state()

    def record_state(self):
        """Saves the current state to history for Monte Carlo analysis."""
        self.history.append({
            'balance': self.balance,
            'debt': self.debt,
            'attention': self.attention,
            'stress_ratio': (self.obligations + self.calculate_debt_service()) / max(1, self.balance + self.income)
        })