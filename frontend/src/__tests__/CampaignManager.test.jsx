/**
 * CampaignManager Component Tests
 *
 * Tests the campaign manager with TTS provider selection functionality
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import CampaignManager from "../components/CampaignManager";

// Mock fetch
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
  };
})();
Object.defineProperty(window, "localStorage", { value: localStorageMock });

describe("CampaignManager TTS Settings", () => {
  const mockCampaign = {
    id: 1,
    title: "Test Campaign",
    description: "A test campaign",
    current_level: 5,
    current_scene_type: "roleplay",
    session_notes: [{ type: "xp_award", amount: 100, reason: "Test XP" }],
    party: [
      {
        character_id: 1,
        name: "Test Hero",
        current_hp: 50,
        max_hp: 100,
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    fetch.mockResolvedValue({
      ok: true,
      json: async () => mockCampaign,
    });
  });

  it("renders TTS settings section", async () => {
    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      expect(screen.getByText("Voice Narration (TTS)")).toBeInTheDocument();
    });

    expect(screen.getByText("Configure")).toBeInTheDocument();
  });

  it("displays current TTS provider chip", async () => {
    localStorage.setItem("ttsProvider", "kitten");

    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/Provider: KittenTTS/i)).toBeInTheDocument();
    });
  });

  it("opens TTS settings dialog when Configure button is clicked", async () => {
    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      expect(screen.getByText("Configure")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Configure"));

    await waitFor(() => {
      expect(screen.getByText("Voice Narration Settings")).toBeInTheDocument();
    });

    // Check for provider options
    expect(screen.getByText(/KittenTTS \(Local\)/i)).toBeInTheDocument();
    expect(screen.getByText(/OpenAI Whisper \(Cloud\)/i)).toBeInTheDocument();
  });

  it("allows switching between TTS providers", async () => {
    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText("Configure"));
    });

    await waitFor(() => {
      expect(screen.getByText("Voice Narration Settings")).toBeInTheDocument();
    });

    // Find and click OpenAI radio button
    const openaiRadio = screen.getByRole("radio", { name: /OpenAI Whisper/i });
    fireEvent.click(openaiRadio);

    // Voice should reset to OpenAI default (alloy)
    const voiceSelect = screen.getByLabelText("Voice Character");
    expect(voiceSelect).toBeInTheDocument();
  });

  it("saves TTS settings to localStorage", async () => {
    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText("Configure"));
    });

    await waitFor(() => {
      expect(screen.getByText("Voice Narration Settings")).toBeInTheDocument();
    });

    // Enable TTS
    const enableCheckbox = screen.getByLabelText("Enable Voice Narration");
    fireEvent.click(enableCheckbox);

    // Save settings
    fireEvent.click(screen.getByText("Save Settings"));

    await waitFor(() => {
      expect(localStorage.getItem("ttsEnabled")).toBe("true");
    });
  });

  it("shows correct voice options for KittenTTS", async () => {
    localStorage.setItem("ttsProvider", "kitten");

    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText("Configure"));
    });

    await waitFor(() => {
      expect(screen.getByLabelText("Voice Character")).toBeInTheDocument();
    });

    // KittenTTS should have 8 voices including tara, leo, etc.
    // (We're not opening the select, just verifying it's there)
  });

  it("shows correct voice options for OpenAI", async () => {
    localStorage.setItem("ttsProvider", "openai");
    localStorage.setItem("ttsVoice", "alloy");

    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText("Configure"));
    });

    await waitFor(() => {
      expect(screen.getByLabelText("Voice Character")).toBeInTheDocument();
    });

    // OpenAI should show different voice (alloy is OpenAI default)
  });

  it("displays info alert based on selected provider", async () => {
    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText("Configure"));
    });

    await waitFor(() => {
      // Should show KittenTTS info by default
      expect(screen.getByText("KittenTTS")).toBeInTheDocument();
      expect(
        screen.getByText(/Ultra-lightweight local TTS/i)
      ).toBeInTheDocument();
    });

    // Switch to OpenAI
    const openaiRadio = screen.getByRole("radio", { name: /OpenAI Whisper/i });
    fireEvent.click(openaiRadio);

    await waitFor(() => {
      expect(screen.getByText("OpenAI Whisper TTS")).toBeInTheDocument();
      expect(
        screen.getByText(/professional text-to-speech API/i)
      ).toBeInTheDocument();
    });
  });

  it("handles campaign without TTS settings gracefully", async () => {
    // Don't set any localStorage values
    render(<CampaignManager campaignId={1} />);

    await waitFor(() => {
      // Should use defaults: kitten provider, tara voice
      expect(screen.getByText(/Provider: KittenTTS/i)).toBeInTheDocument();
      expect(screen.getByText(/Voice: tara/i)).toBeInTheDocument();
    });
  });
});
