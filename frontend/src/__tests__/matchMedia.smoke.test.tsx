import React from "react";
import { render, screen } from "@testing-library/react";
import Button from "@mui/material/Button";
import useMediaQuery from "@mui/material/useMediaQuery";

function MediaTestComponent() {
  const isSmall = useMediaQuery("(max-width:600px)");
  return React.createElement(
    "div",
    null,
    React.createElement(Button, { variant: "contained" }, "Hello"),
    React.createElement(
      "span",
      { "data-testid": "mq" },
      isSmall ? "small" : "not-small"
    )
  );
}

test("matchMedia mock allows MUI hooks to run and component renders", () => {
  render(React.createElement(MediaTestComponent));
  expect(screen.getByText("Hello")).toBeInTheDocument();
  const mq = screen.getByTestId("mq");
  expect(mq.textContent).toBe("not-small");
});
