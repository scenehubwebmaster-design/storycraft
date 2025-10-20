import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import React from "react";
import { render } from "@testing-library/react";

// We'll mock react-leaflet's useMap dynamically in beforeEach so we can inject our mockMap.

// Create a mock leaflet module
const addLayer = vi.fn();
const removeLayer = vi.fn();
const hasLayer = vi.fn(() => true);

const mockMap = {
  addLayer,
  removeLayer,
  hasLayer,
};

// Minimal marker cluster group mock
const mockClusterGroup = {
  addLayer: vi.fn(),
  removeLayer: vi.fn(),
};

// Mock marker creation
const mockMarker = vi.fn(() => ({ bindPopup: vi.fn() }));

// Mock leaflet so that both the default export and named exports provide
// markerClusterGroup and marker. The component imports the default (L),
// and tests use require('leaflet') which may reference named exports.
vi.mock("leaflet", () => {
  const fn = vi.fn(() => mockClusterGroup);
  return {
    __esModule: true,
    default: {
      markerClusterGroup: fn,
      marker: mockMarker,
    },
    markerClusterGroup: fn,
    marker: mockMarker,
  };
});

describe("MapClusterGroup", () => {
  beforeEach(() => {
    vi.doMock("react-leaflet", () => ({
      useMap: () => mockMap,
    }));
    addLayer.mockClear();
    removeLayer.mockClear();
    mockClusterGroup.addLayer.mockClear();
    mockClusterGroup.removeLayer.mockClear();
    mockMarker.mockClear();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("creates cluster group and markers and cleans up on unmount", async () => {
    const { default: MapClusterGroup } = await import(
      "../components/MapClusterGroup.jsx"
    );

    const markers = [
      { id: 1, name: "A", lat: 10, lng: 10 },
      { id: 2, name: "B", lat: 11, lng: 11 },
    ];

    const { unmount } = render(<MapClusterGroup markers={markers} />);

    // cluster group should be created and added to map (map.addLayer called)
    expect(addLayer).toHaveBeenCalled();
    // markers created and added to cluster
    expect(mockMarker).toHaveBeenCalledTimes(2);
    expect(mockClusterGroup.addLayer).toHaveBeenCalledTimes(2);

    // unmount -> cleanup
    unmount();
    expect(mockClusterGroup.removeLayer).toHaveBeenCalled();
    expect(removeLayer).toHaveBeenCalled();
  });
});
