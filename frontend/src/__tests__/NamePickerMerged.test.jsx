import React from "react";
import { render, screen } from "@testing-library/react";
import NamePicker from "../components/NamePicker";

describe("NamePicker merged suggestions", () => {
  it("renders merged name suggestions from top-level and structured data", () => {
    const merged = [
      { first_name: "Alric", surname: "Storm", _ai: true },
      { first_name: "Bren", surname: "Oak", _ai: false },
    ];

    render(<NamePicker nameOptions={merged} />);

    // Expect chips for both names to be present
    expect(screen.getByText("Alric Storm")).toBeInTheDocument();
    expect(screen.getByText("Bren Oak")).toBeInTheDocument();
  });
});
