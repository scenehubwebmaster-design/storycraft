import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ReferenceViewer from "../components/ReferenceViewer";
import { ThemeProvider, createTheme } from "@mui/material/styles";

// Mock fetch responses for two ref types
const classItems = [
  { id: 1, title: "Fighter", key: "fighter", content: "Fighter content" },
];
const speciesItems = [
  { id: 2, title: "Elf", key: "elf", content: "Elf content" },
];

const renderWithTheme = (ui, options) =>
  render(<ThemeProvider theme={createTheme()}>{ui}</ThemeProvider>, options);

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    if (url.includes("ref_type=class")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(classItems),
      });
    }
    if (url.includes("ref_type=species")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(speciesItems),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
  });
});

afterEach(() => {
  vi.resetAllMocks();
});

test("preserves selection when switching to a type that contains the same id (none here)", async () => {
  // Render with initial type 'class'
  const { rerender } = renderWithTheme(<ReferenceViewer refType="class" />);

  // Wait for list item to appear
  await waitFor(() => expect(screen.getByText("Fighter")).toBeInTheDocument());

  // Click the item to select
  userEvent.click(screen.getByText("Fighter"));

  // Detail should appear
  await waitFor(() =>
    expect(screen.getByText("Fighter content")).toBeInTheDocument()
  );

  // Rerender with species (different items) - parent switching would mount new prop
  rerender(
    <ThemeProvider theme={createTheme()}>
      <ReferenceViewer refType="species" />
    </ThemeProvider>
  );

  // Species list should appear
  await waitFor(() => expect(screen.getByText("Elf")).toBeInTheDocument());

  // Since the previous selection id (1) is not in species, details should not show fighter content
  expect(screen.queryByText("Fighter content")).not.toBeInTheDocument();
});

test("keeps selection when re-rendered with same type", async () => {
  const { rerender } = renderWithTheme(<ReferenceViewer refType="class" />);

  await waitFor(() => expect(screen.getByText("Fighter")).toBeInTheDocument());
  userEvent.click(screen.getByText("Fighter"));
  await waitFor(() =>
    expect(screen.getByText("Fighter content")).toBeInTheDocument()
  );

  // Rerender with same type; selection should persist
  rerender(
    <ThemeProvider theme={createTheme()}>
      <ReferenceViewer refType="class" />
    </ThemeProvider>
  );
  expect(screen.getByText("Fighter content")).toBeInTheDocument();
});
