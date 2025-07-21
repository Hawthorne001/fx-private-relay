import {
  ProfileData,
  ProfileUpdateFn,
  SetSubdomainFn,
  useProfiles,
} from "../../../src/hooks/api/profile";

jest.mock("../../../src/hooks/api/profile");

// We know that `jest.mock` has turned `useProfiles` into a mock function,
// but TypeScript can't — so we tell it using a type assertion:
const mockedUseProfiles = useProfiles as jest.MockedFunction<
  typeof useProfiles
>;

type MockData = Partial<ProfileData>;

export function getMockProfileData(profileData?: MockData): ProfileData {
  return {
    has_premium: false,
    has_phone: false,
    has_vpn: false,
    has_megabundle: false,
    store_phone_log: true,
    id: 0,
    server_storage: true,
    remove_level_one_email_trackers: false,
    subdomain: null,
    onboarding_state: 3,
    onboarding_free_state: 3,
    forwarded_first_reply: true,
    avatar: "",
    date_subscribed: null,
    bounce_status: [false, ""],
    next_email_try: "2022-04-02T13:37:00Z",
    api_token: "",
    emails_blocked: 0,
    emails_forwarded: 0,
    emails_replied: 0,
    level_one_trackers_blocked: 0,
    metrics_enabled: false,
    ...profileData,
  };
}

type Callbacks = {
  updater?: ProfileUpdateFn;
  setSubdomain: SetSubdomainFn;
};
function getReturnValue(
  profileData?: MockData | null,
  callbacks?: Callbacks,
): ReturnType<typeof useProfiles> {
  return {
    isValidating: false,
    mutate: jest.fn(),
    update: callbacks?.updater ?? jest.fn(),
    data: profileData === null ? undefined : [getMockProfileData(profileData)],
    setSubdomain: callbacks?.setSubdomain ?? jest.fn(),
    isLoading: false,
    error: undefined,
  };
}

export const setMockProfileData = (
  profileData?: MockData | null,
  callbacks?: Callbacks,
) => {
  mockedUseProfiles.mockReturnValue(getReturnValue(profileData, callbacks));
};

export const setMockProfileDataOnce = (
  profileData?: MockData | null,
  callbacks?: Callbacks,
) => {
  mockedUseProfiles.mockReturnValueOnce(getReturnValue(profileData, callbacks));
};
