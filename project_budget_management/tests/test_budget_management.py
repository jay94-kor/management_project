import unittest
from budget_management import add_project, get_project_budget, record_transaction

class TestBudgetManagement(unittest.TestCase):
    def test_add_project(self):
        add_project("Test Project", 1000)
        budget = get_project_budget(1)
        self.assertEqual(budget['assigned_budget'], 1000)

    def test_record_transaction(self):
        add_project("Test Project", 1000)
        record_transaction(1, "Test Transaction", 200, "2024-07-11")
        budget = get_project_budget(1)
        self.assertEqual(budget['spent_budget'], 200)
        self.assertEqual(budget['remaining_budget'], 800)

if __name__ == '__main__':
    unittest.main()
