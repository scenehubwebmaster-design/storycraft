import React from "react";
import { render, screen } from "@testing-library/react";
import RagTesterPage from "../pages/RagTester";

test("renders RAG Tester header", () => {
  render(<RagTesterPage />);
  expect(screen.getByText(/RAG Tester/i)).toBeInTheDocument();
});
