import { render, screen } from "@testing-library/react";
import PhoneWaitlist from "../../../src/pages/phone/waitlist.page";
import { useL10n } from "../../../src/hooks/l10n";
import { WaitlistPage } from "../../../src/components/waitlist/WaitlistPage";

// Mock Localized to avoid needing <LocalizationProvider>
jest.mock("../../../src/components/Localized", () => ({
  Localized: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

jest.mock("../../../src/hooks/l10n");
jest.mock("../../../src/components/waitlist/WaitlistPage", () => ({
  WaitlistPage: jest.fn(() => <div data-testid="mock-waitlist-page" />),
}));

describe("PhoneWaitlist page", () => {
  const mockGetString = jest.fn();

  beforeEach(() => {
    (useL10n as jest.Mock).mockReturnValue({
      getString: mockGetString,
    });

    mockGetString.mockImplementation((id: string) => {
      const strings: Record<string, string> = {
        "waitlist-heading-phone": "Get a private phone number",
        "waitlist-lead-phone": "Be the first to try Relay phone masking",
        "waitlist-privacy-policy-use-phone":
          "We will use your phone only to notify you.",
      };
      return strings[id] ?? id;
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the WaitlistPage with correct props", () => {
    render(<PhoneWaitlist />);

    const props = (WaitlistPage as jest.Mock).mock.calls[0][0];

    expect(props.supportedLocales).toEqual(["en", "es", "pl", "pt", "ja"]);
    expect(props.headline).toBe("Get a private phone number");
    expect(props.lead).toBe("Be the first to try Relay phone masking");
    expect(props.newsletterId).toBe("relay-phone-masking-waitlist");
    expect(props.legalese).toBeDefined();

    expect(screen.getByTestId("mock-waitlist-page")).toBeInTheDocument();
  });

  it("renders legalese content", () => {
    render(<PhoneWaitlist />);
    const legalese = (WaitlistPage as jest.Mock).mock.calls[0][0].legalese;

    render(<>{legalese}</>);

    expect(
      screen.getByText("We will use your phone only to notify you."),
    ).toBeInTheDocument();
  });
});
