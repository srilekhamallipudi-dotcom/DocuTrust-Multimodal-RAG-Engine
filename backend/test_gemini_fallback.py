import unittest

from gemini_service import fallback_answer_from_context


class GeminiFallbackTests(unittest.TestCase):
    def test_extracts_candidate_name(self):
        context = "Candidate Name: John Doe\nCareer Objective: Build impactful AI products."
        answer = fallback_answer_from_context(context, "What is the candidate name?")
        self.assertIn("John Doe", answer)

    def test_extracts_career_objective(self):
        context = "CAREER OBJECTIVE:\nSeeking an internship to apply technical knowledge and gain practical experience."
        answer = fallback_answer_from_context(context, "What is the candidate's career objective?")
        self.assertIn("internship", answer.lower())

    def test_returns_not_enough_information(self):
        context = "This document contains only a list of unrelated technical topics."
        answer = fallback_answer_from_context(context, "What is the candidate name?")
        self.assertIn("Not enough information", answer)


if __name__ == "__main__":
    unittest.main()
