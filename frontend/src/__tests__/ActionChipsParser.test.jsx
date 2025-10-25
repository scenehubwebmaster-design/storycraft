import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ActionChipsParser from "../components/game/ActionChipsParser";

describe("ActionChipsParser", () => {
  describe("Bold text actions", () => {
    it("should parse bold text actions and render clickable chips", () => {
      const content = `
The night air in Breezewood carries the scent of pine. Inside the Gilded Griffon tavern, a weathered half-elf sits beneath a banner.

**Approach Rorik** – Introduce yourself and ask about the map.
**Inspect the parchment** – Take a closer look at the map.
**Talk to Mira** – Order a drink from the halfling barkeep.
      `;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      // Verify that action chips are rendered
      expect(screen.getByText(/Approach Rorik/i)).toBeInTheDocument();
      expect(screen.getByText(/Inspect the parchment/i)).toBeInTheDocument();
      expect(screen.getByText(/Talk to Mira/i)).toBeInTheDocument();
    });

    it("should call onActionClick when a bold action chip is clicked", () => {
      const content = "**Approach Rorik** – Introduce yourself.";
      const onActionClick = vi.fn();

      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      const chip = screen
        .getByText(/Approach Rorik/i)
        .closest('div[role="button"]');
      fireEvent.click(chip);

      expect(onActionClick).toHaveBeenCalledWith(
        "Approach Rorik",
        undefined,
        undefined
      );
    });

    it("should not parse stat headings as actions", () => {
      const content = `
**AC: 15** | **HP: 25/30** | **Speed: 30 ft**

**STR: +2** | **DEX: +3** | **CON: +1**
      `;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      // Stats should not be rendered as action chips
      expect(screen.queryByText(/AC: 15/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/HP: 25/i)).not.toBeInTheDocument();
    });

    it("should truncate long action labels", () => {
      const longAction = "A".repeat(60);
      const content = `**${longAction}** – Description`;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      // Should show truncated version with ellipsis
      const chipText = screen.getByText(/A{50}\.\.\./, { exact: false });
      expect(chipText).toBeInTheDocument();
    });
  });

  describe("Table-based actions", () => {
    it("should parse action tables and render clickable chips", () => {
      const content = `
| Action | Suggested Roll | DC (if applicable) |
|--------|----------------|-------------------|
| Perception check to spot details | d20 + Perception | 12 (to notice) |
| Insight check to read intentions | d20 + Insight | 14 (to discern) |
      `;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      expect(screen.getByText(/Perception check/i)).toBeInTheDocument();
      expect(screen.getByText(/Insight check/i)).toBeInTheDocument();
      expect(screen.getByText(/d20 \+ Perception/i)).toBeInTheDocument();
    });

    it("should call onActionClick with roll and DC for table actions", () => {
      const content = `
| Action | Suggested Roll | DC |
|--------|----------------|-----|
| Perception check | d20 + Perception | 12 |
      `;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      const chip = screen
        .getByText(/Perception check/i)
        .closest('div[role="button"]');
      fireEvent.click(chip);

      expect(onActionClick).toHaveBeenCalledWith(
        "Perception check",
        "d20 + Perception",
        "12"
      );
    });
  });

  describe("Mixed content", () => {
    it("should handle both bold actions and table actions", () => {
      const content = `
**Quick Action** – Do something fast.

| Action | Suggested Roll | DC |
|--------|----------------|-----|
| Detailed check | d20 + Insight | 15 |
      `;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      expect(screen.getByText(/Quick Action/i)).toBeInTheDocument();
      expect(screen.getByText(/Detailed check/i)).toBeInTheDocument();
    });
  });

  describe("Empty or invalid content", () => {
    it("should return null when no actions are found", () => {
      const content = "Just some regular narrative text without any actions.";

      const onActionClick = vi.fn();
      const { container } = render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      expect(container.firstChild).toBeNull();
    });

    it("should handle empty content gracefully", () => {
      const onActionClick = vi.fn();
      const { container } = render(
        <ActionChipsParser content="" onActionClick={onActionClick} />
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe("Duplicate prevention", () => {
    it("should not render duplicate bold actions", () => {
      const content = `
**Approach Rorik** – First mention.
**Approach Rorik** – Second mention.
      `;

      const onActionClick = vi.fn();
      render(
        <ActionChipsParser content={content} onActionClick={onActionClick} />
      );

      // Should only render one chip for "Approach Rorik"
      const chips = screen.getAllByText(/Approach Rorik/i);
      expect(chips).toHaveLength(1);
    });
  });
});
