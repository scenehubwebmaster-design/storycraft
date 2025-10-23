/**
 * TTSAudioPlayer Component Tests
 *
 * Tests the TTS audio player component with flavor text toggle functionality
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TTSAudioPlayer from "../components/game/TTSAudioPlayer";
import axios from "axios";

// Mock axios
vi.mock("axios");

// Mock URL.createObjectURL and URL.revokeObjectURL
global.URL.createObjectURL = vi.fn(() => "blob:mock-url");
global.URL.revokeObjectURL = vi.fn();

describe("TTSAudioPlayer", () => {
  const mockSessionId = "session-123";
  const mockMessageId = "message-456";

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock axios.post to return a blob
    axios.post.mockResolvedValue({
      data: new Blob(["mock audio data"], { type: "audio/wav" }),
    });
  });

  it("renders compact mode without voice selector", () => {
    render(
      <TTSAudioPlayer
        sessionId={mockSessionId}
        messageId={mockMessageId}
        compact={true}
      />
    );

    // Should have play button
    const playButton = screen.getByRole("button");
    expect(playButton).toBeDefined();
  });

  it("renders with voice selector when showVoiceSelector is true", () => {
    render(
      <TTSAudioPlayer
        sessionId={mockSessionId}
        messageId={mockMessageId}
        showVoiceSelector={true}
      />
    );

    // Should have voice selector
    expect(screen.getByLabelText(/DM Voice/i)).toBeDefined();
  });

  it("renders RP Text Only checkbox when voice selector is shown", () => {
    render(
      <TTSAudioPlayer
        sessionId={mockSessionId}
        messageId={mockMessageId}
        showVoiceSelector={true}
      />
    );

    // Should have the RP Text Only checkbox
    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeDefined();
    expect(screen.getByText(/RP Text Only/i)).toBeDefined();
  });

  it("sends flavor_text_only=false by default when fetching audio", async () => {
    render(
      <TTSAudioPlayer sessionId={mockSessionId} messageId={mockMessageId} />
    );

    // Click play to fetch audio
    const playButton = screen.getByRole("button");
    fireEvent.click(playButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining("flavor_text_only=false"),
        expect.anything(),
        expect.anything()
      );
    });
  });

  it("sends flavor_text_only=true when checkbox is checked", async () => {
    render(
      <TTSAudioPlayer
        sessionId={mockSessionId}
        messageId={mockMessageId}
        showVoiceSelector={true}
      />
    );

    // Check the RP Text Only checkbox
    const checkbox = screen.getByRole("checkbox");
    fireEvent.click(checkbox);

    // Click play to fetch audio
    const playButton = screen.getByRole("button", { name: /play/i });
    fireEvent.click(playButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining("flavor_text_only=true"),
        expect.anything(),
        expect.anything()
      );
    });
  });

  it("refetches audio when flavor text toggle changes", async () => {
    render(
      <TTSAudioPlayer
        sessionId={mockSessionId}
        messageId={mockMessageId}
        showVoiceSelector={true}
      />
    );

    // First, fetch audio by clicking play
    const playButton = screen.getByRole("button", { name: /play/i });
    fireEvent.click(playButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledTimes(1);
    });

    // Now toggle the checkbox
    const checkbox = screen.getByRole("checkbox");
    fireEvent.click(checkbox);

    // Should trigger another fetch
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledTimes(2);
      expect(axios.post).toHaveBeenLastCalledWith(
        expect.stringContaining("flavor_text_only=true"),
        expect.anything(),
        expect.anything()
      );
    });
  });

  it("includes selected voice in API call", async () => {
    render(
      <TTSAudioPlayer
        sessionId={mockSessionId}
        messageId={mockMessageId}
        showVoiceSelector={true}
      />
    );

    // Click play to fetch audio
    const playButton = screen.getByRole("button", { name: /play/i });
    fireEvent.click(playButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringMatching(/voice=tara/),
        expect.anything(),
        expect.anything()
      );
    });
  });
});
