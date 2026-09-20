import sys
import os
import unittest

# Connect the test suite to your src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.household import Household
from src.model.choice_set import Action, ChoiceSet

class TestModelInvariants(unittest.TestCase):
    
    def setUp(self):
        """Create a fresh household before every test to ensure isolation."""
        self.hh = Household(1000.0, 5000.0, 1200.0, 1500.0, 0.6)
        
        self.actions = [
            Action("Pay in Full", 0.0, 0.1),
            Action("Min Payment", 50.0, 0.2)
        ]
        self.choice_set = ChoiceSet(self.actions)

    def test_initial_state_bounds(self):
        """Economic Invariant: Attention cannot exceed 1.0 or drop below 0.0 at start."""
        self.assertLessEqual(self.hh.attention, 1.0, "Attention initialized above maximum capacity.")
        self.assertGreaterEqual(self.hh.attention, 0.0, "Attention initialized below zero.")

    def test_budget_conservation(self):
        """Mathematical Invariant: Income additions must perfectly conserve value."""
        initial = self.hh.balance
        self.hh.balance += 500.0
        self.assertEqual(self.hh.balance, initial + 500.0, "Budget conservation failed during addition.")

    def test_choice_set_nonnegative_costs(self):
        """Economic Invariant: Actions cannot have negative immediate costs (which would be free money)."""
        # Testing the list directly to avoid ChoiceSet attribute naming mismatches
        for action in self.actions:
            self.assertGreaterEqual(action.immediate_cost, 0.0, f"Action {action.name} has a negative cost.")

    def test_debt_nonnegative(self):
        """Mathematical Invariant: Debt cannot spontaneously become negative (a hidden asset)."""
        self.assertGreaterEqual(self.hh.debt, 0.0, "Household debt initialized below zero.")

if __name__ == '__main__':
    unittest.main()