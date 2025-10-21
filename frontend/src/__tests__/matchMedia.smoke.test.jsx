import React from "react";
import { render, screen } from "@testing-library/react";
import Button from "@mui/material/Button";
import useMediaQuery from "@mui/material/useMediaQuery";

function MediaTestComponent() {
  const isSmall = useMediaQuery("(max-width:600px)");
  return (
    <div>
      <Button variant="contained">Hello</Button>
      <span data-testid="mq">{isSmall ? "small" : "not-small"}</span>
    </div>
  );
}

test("matchMedia mock allows MUI hooks to run and component renders", () => {
  render(<MediaTestComponent />);
  expect(screen.getByText("Hello")).toBeInTheDocument();
  const mq = screen.getByTestId("mq");
  expect(mq.textContent).toBe("not-small");
});
