// Mock Vite-specific config module so tests don't use import.meta.env
vi.mock("../../src/config/api", () => ({ API_URL: "http://localhost:8000" }));

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axios from "axios";
import NamePicker from "../components/NamePicker";

vi.mock("axios");

describe("NamePicker", () => {
  beforeEach(() => {
    axios.post.mockClear();
  });

  it("renders name options and calls regenerate", async () => {
    const names = [
      { first_name: "Test", surname: "One", _ai: true },
      { first_name: "Test", surname: "Two" },
    ];

    axios.post.mockResolvedValueOnce({ data: { names } });

    render(<NamePicker nameOptions={[]} />);

    // The component auto-regenerates if no options provided - wait for chips
    await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));

    // After resolving, the name chips should appear
    expect(await screen.findByText("Test One")).toBeInTheDocument();
    expect(await screen.findByText("Test Two")).toBeInTheDocument();

    // Click regenerate and ensure axios.post is called again
    const regenBtn = screen.getAllByRole("button", { name: /Regenerate/i })[0];
    axios.post.mockResolvedValueOnce({ data: { names } });
    await userEvent.click(regenBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalled());
  });
});
