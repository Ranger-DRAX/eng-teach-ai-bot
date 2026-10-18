import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "../src/app/page";

describe("Frontend Smoke Tests", () => {
  it("renders the landing title", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toBeDefined();
    expect(screen.getByText("English Learning Chatbot")).toBeDefined();
  });

  it("has navigation buttons", () => {
    render(<Home />);
    expect(screen.getByText(/Start Learning/i)).toBeDefined();
    expect(screen.getByText(/Parent Dashboard/i)).toBeDefined();
  });
});
