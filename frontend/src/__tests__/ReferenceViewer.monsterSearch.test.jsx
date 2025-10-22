import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ReferenceViewer from "../components/ReferenceViewer";

global.fetch = vi.fn();

test("monster search is called and results render for species", async () => {
  fetch.mockImplementation((url) => {
    if (url.includes("/api/monsters/search")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([{ id: 1, name: "Goblin", cr: 0.25, ac: 15, hp: 7 }]),
      });
    }
    // default references call
    return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
  });

  render(<ReferenceViewer refType="species" />);

  // find monster search input and type
  const monsterInput = await screen.findByPlaceholderText(/Search monsters/i);
  fireEvent.change(monsterInput, { target: { value: "gob" } });

  // click the Search button
  const searchBtn = await screen.findByRole("button", { name: /Search/i });
  fireEvent.click(searchBtn);

  await waitFor(() =>
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/monsters/search?q=")
    )
  );

  // Expect the results to be present in the DOM
  await screen.findByText(/Goblin/i);

  // click the monster result and expect detail pane to show CR/AC/HP
  const monsterResult = await screen.findByText(/Goblin/i);
  fireEvent.click(monsterResult);
  await screen.findByText(/CR:/i);
});
