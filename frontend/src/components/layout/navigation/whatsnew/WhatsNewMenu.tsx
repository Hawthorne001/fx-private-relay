import {
  forwardRef,
  HTMLAttributes,
  ReactNode,
  RefObject,
  useRef,
} from "react";
import {
  DismissButton,
  FocusScope,
  mergeProps,
  OverlayContainer,
  useButton,
  useDialog,
  useModal,
  useOverlay,
  useOverlayPosition,
  useOverlayTrigger,
} from "react-aria";
import { useOverlayTriggerState } from "react-stately";
import { StaticImageData } from "next/image";
import styles from "./WhatsNewMenu.module.scss";
import SizeLimitHero from "./images/size-limit-hero-10mb.svg";
import SizeLimitIcon from "./images/size-limit-icon-10mb.svg";
import SignBackInHero from "./images/sign-back-in-hero.svg";
import SignBackInIcon from "./images/sign-back-in-icon.svg";
import ForwardSomeHero from "./images/forward-some-hero.svg";
import ForwardSomeIcon from "./images/forward-some-icon.svg";
import aliasToMaskHero from "./images/alias-to-mask-hero.svg";
import aliasToMaskIcon from "./images/alias-to-mask-icon.svg";
import TrackerRemovalHero from "./images/tracker-removal-hero.svg";
import TrackerRemovalIcon from "./images/tracker-removal-icon.svg";
import PremiumSwedenHero from "./images/premium-expansion-sweden-hero.svg";
import PremiumSwedenIcon from "./images/premium-expansion-sweden-icon.svg";
import PremiumEuExpansionHero from "./images/eu-expansion-hero.svg";
import PremiumEuExpansionIcon from "./images/eu-expansion-icon.svg";
import PremiumFinlandHero from "./images/premium-expansion-finland-hero.svg";
import PremiumFinlandIcon from "./images/premium-expansion-finland-icon.svg";
import PhoneMaskingHero from "./images/phone-masking-hero.svg";
import PhoneMaskingIcon from "./images/phone-masking-icon.svg";
import HolidayPromo2023Icon from "./images/holiday-promo-2023-news-icon.svg";
import HolidayPromo2023Hero from "./images/holiday-promo-2023-news-hero.svg";
import BundleHero from "./images/bundle-promo-hero.svg";
import BundleIcon from "./images/bundle-promo-icon.svg";
import FirefoxIntegrationHero from "./images/firefox-integration-hero.svg";
import FirefoxIntegrationIcon from "./images/firefox-integration-icon.svg";
import MailingListHero from "./images/mailing-list-hero.svg";
import MailingListIcon from "./images/mailing-list-icon.svg";
import ShieldHero from "./images/shield-hero.svg";
import ShieldIcon from "./images/shield-icon.svg";
import { WhatsNewContent } from "./WhatsNewContent";
import {
  DismissalData,
  useLocalDismissal,
} from "../../../../hooks/localDismissal";
import { ProfileData } from "../../../../hooks/api/profile";
import { WhatsNewDashboard } from "./WhatsNewDashboard";
import { useAddonData } from "../../../../hooks/addon";
import { isUsingFirefox } from "../../../../functions/userAgent";
import { getLocale } from "../../../../functions/getLocale";
import { RuntimeData } from "../../../../hooks/api/runtimeData";
import { isFlagActive } from "../../../../functions/waffle";
import {
  getBundlePrice,
  getMegabundlePrice,
  getMegabundleSubscribeLink,
  getPeriodicalPremiumSubscribeLink,
  isBundleAvailableInCountry,
  isMegabundleAvailableInCountry,
  isPeriodicalPremiumAvailableInCountry,
  isPhonesAvailableInCountry,
} from "../../../../functions/getPlan";
import Link from "next/link";
import { GiftIcon } from "../../../Icons";
import { useGaEvent } from "../../../../hooks/gaEvent";
import { useL10n } from "../../../../hooks/l10n";
import { VisuallyHidden } from "../../../VisuallyHidden";
import { useOverlayBugWorkaround } from "../../../../hooks/overlayBugWorkaround";
import { useGaViewPing } from "../../../../hooks/gaViewPing";

export type WhatsNewEntry = {
  title: string;
  snippet: string;
  content: ReactNode;
  icon: StaticImageData;
  dismissal: DismissalData;
  /**
   * This is used to automatically archive entries of a certain age
   */
  announcementDate: {
    year: number;
    // Spelled out just to make sure it's clear we're not using 0-based months.
    // Thanks, JavaScript...
    month: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
    day: number;
  };
};

export type Props = {
  profile: ProfileData;
  style: string;
  runtimeData?: RuntimeData;
};

type CtaProps = {
  link?: string;
  label: string;
  subscribed?: boolean;
};

const CtaLinkButton = (props: CtaProps) => {
  const hasSubscription = props.subscribed;

  return (
    <>
      {!hasSubscription ? (
        <Link href="/premium#pricing" legacyBehavior>
          <span className={styles.cta}>{props.label}</span>
        </Link>
      ) : null}
    </>
  );
};

export const WhatsNewMenu = (props: Props) => {
  const l10n = useL10n();
  const gaEvent = useGaEvent();

  const triggerState = useOverlayTriggerState({
    onOpenChange(isOpen) {
      gaEvent({
        category: "News",
        action: isOpen ? "Open" : "Close",
        label: "header-nav",
      });
    },
  });

  const triggerRef = useRef<HTMLButtonElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  const addonData = useAddonData();

  const entries: WhatsNewEntry[] = [
    {
      title: l10n.getString("whatsnew-feature-size-limit-heading"),
      snippet: l10n.getString("whatsnew-feature-size-limit-snippet-var", {
        size: 10,
        unit: "MB",
      }),
      content: (
        <WhatsNewContent
          description={l10n.getString(
            "whatsnew-feature-size-limit-description-var",
            {
              size: 10,
              unit: "MB",
            },
          )}
          heading={l10n.getString("whatsnew-feature-size-limit-heading")}
          image={SizeLimitHero}
          videos={{
            // Unfortunately video files cannot currently be imported, so make
            // sure these files are present in /public. See
            // https://github.com/vercel/next.js/issues/35248
            "video/webm; codecs='vp9'":
              "/animations/whatsnew/size-limit-hero-10mb.webm",
            "video/mp4": "/animations/whatsnew/size-limit-hero-10mb.mp4",
          }}
        />
      ),
      icon: SizeLimitIcon,
      dismissal: useLocalDismissal(
        `whatsnew-feature_size-limit_${props.profile.id}`,
      ),
      announcementDate: {
        year: 2022,
        month: 3,
        day: 1,
      },
    },
  ];

  const forwardSomeEntry: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-forward-some-heading"),
    snippet: l10n.getString("whatsnew-feature-forward-some-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-forward-some-description",
        )}
        heading={l10n.getString("whatsnew-feature-forward-some-heading")}
        image={ForwardSomeHero}
      />
    ),
    icon: ForwardSomeIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_sign-back-in_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2022,
      month: 3,
      day: 1,
    },
  };
  if (props.profile.has_premium) {
    entries.push(forwardSomeEntry);
  }

  const signBackInEntry: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-sign-back-in-heading"),
    snippet: l10n.getString("whatsnew-feature-sign-back-in-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-sign-back-in-description",
        )}
        heading={l10n.getString("whatsnew-feature-sign-back-in-heading")}
        image={SignBackInHero}
      />
    ),
    icon: SignBackInIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_sign-back-in_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2022,
      month: 2,
      day: 1,
    },
  };
  if (addonData.present && isUsingFirefox()) {
    entries.push(signBackInEntry);
  }

  const aliasToMask: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-alias-to-mask-heading"),
    snippet: l10n.getString("whatsnew-feature-alias-to-mask-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-alias-to-mask-description",
        )}
        heading={l10n.getString("whatsnew-feature-alias-to-mask-heading")}
        image={aliasToMaskHero}
      />
    ),
    icon: aliasToMaskIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_alias-to-mask_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2022,
      month: 4,
      day: 19,
    },
  };
  // Not all localisations transitioned from "alias" to "mask", so only show this
  // announcement for those of which we _know_ did:
  if (
    [
      "en",
      "en-gb",
      "nl",
      "fy-nl",
      "zh-tw",
      "es-es",
      "es-mx",
      "de",
      "pt-br",
      "sv-se",
      "el",
      "hu",
      "sk",
      "skr",
      "uk",
    ].includes(getLocale(l10n).toLowerCase())
  ) {
    entries.push(aliasToMask);
  }

  const premiumInSweden: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-premium-expansion-sweden-heading"),
    snippet: l10n.getString("whatsnew-feature-premium-expansion-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-premium-expansion-description",
        )}
        heading={l10n.getString(
          "whatsnew-feature-premium-expansion-sweden-heading",
        )}
        image={PremiumSwedenHero}
      />
    ),
    icon: PremiumSwedenIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_premium-expansion-sweden_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2022,
      month: 5,
      day: 17,
    },
  };
  if (
    props.runtimeData?.PERIODICAL_PREMIUM_PLANS.country_code.toLowerCase() ===
      "se" &&
    !props.profile.has_premium
  ) {
    entries.push(premiumInSweden);
  }

  const premiumInFinland: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-premium-expansion-finland-heading"),
    snippet: l10n.getString("whatsnew-feature-premium-expansion-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-premium-expansion-description",
        )}
        heading={l10n.getString(
          "whatsnew-feature-premium-expansion-finland-heading",
        )}
        image={PremiumFinlandHero}
      />
    ),
    icon: PremiumFinlandIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_premium-expansion-finland_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2022,
      month: 5,
      day: 17,
    },
  };
  if (
    props.runtimeData?.PERIODICAL_PREMIUM_PLANS.country_code.toLowerCase() ===
      "fi" &&
    !props.profile.has_premium
  ) {
    entries.push(premiumInFinland);
  }

  // Check if yearlyPlanLink should be generated based on runtimeData and availability
  const yearlyPlanLink =
    props.runtimeData &&
    isPeriodicalPremiumAvailableInCountry(props.runtimeData)
      ? getPeriodicalPremiumSubscribeLink(props.runtimeData, "yearly")
      : undefined;

  const yearlyPlanRefWithCoupon = `${yearlyPlanLink}&coupon=HOLIDAY20&utm_source=relay.firefox.com&utm_medium=whatsnew-announcement&utm_campaign=relay-holiday-promo-2023`;
  const getYearlyPlanBtnRef = useGaViewPing({
    category: "Holiday Promo News CTA",
    label: "holiday-promo-2023-news-cta",
  });

  const holidayPromo2023: WhatsNewEntry = {
    title: l10n.getString("whatsnew-holiday-promo-2023-news-heading"),
    snippet: l10n.getString("whatsnew-holiday-promo-2023-news-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-holiday-promo-2023-news-content-description",
        )}
        heading={l10n.getString("whatsnew-holiday-promo-2023-news-heading")}
        image={HolidayPromo2023Hero}
        cta={
          <Link
            href={yearlyPlanRefWithCoupon}
            ref={getYearlyPlanBtnRef}
            onClick={() => {
              gaEvent({
                category: "Holiday Promo News CTA",
                action: "Engage",
                label: "holiday-promo-2023-news-cta",
              });
            }}
          >
            <span className={styles.cta}>
              {l10n.getString("whatsnew-holiday-promo-2023-cta")}
            </span>
          </Link>
        }
      />
    ),
    icon: HolidayPromo2023Icon,
    dismissal: useLocalDismissal(
      `whatsnew-holiday_promo_2023_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2023,
      month: 11,
      day: 29,
    },
  };

  // Check if the holiday promotion entry should be added to the entries array
  if (
    isFlagActive(props.runtimeData, "holiday_promo_2023") &&
    !props.profile.has_premium &&
    isPeriodicalPremiumAvailableInCountry(props.runtimeData)
  ) {
    entries.push(holidayPromo2023);
  }

  const premiumEuExpansion: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-premium-expansion-eu-heading"),
    snippet: l10n.getString("whatsnew-feature-premium-expansion-eu-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-premium-expansion-eu-description",
        )}
        heading={l10n.getString(
          "whatsnew-feature-premium-expansion-eu-heading",
        )}
        image={PremiumEuExpansionHero}
        cta={
          <Link href="/premium#pricing" legacyBehavior>
            <span className={styles.cta}>
              {l10n.getString("whatsnew-feature-premium-expansion-eu-cta")}
            </span>
          </Link>
        }
      />
    ),
    icon: PremiumEuExpansionIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_premium-eu-expansion_2023_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2023,
      month: 7,
      day: 26,
    },
  };

  if (
    typeof props.runtimeData !== "undefined" &&
    !props.profile.has_premium &&
    [
      "bg",
      "cz",
      "cy",
      "dk",
      "ee",
      "gr",
      "hr",
      "hu",
      "lt",
      "lv",
      "lu",
      "mt",
      "pl",
      "pt",
      "ro",
      "si",
      "sk",
    ].includes(
      props.runtimeData.PERIODICAL_PREMIUM_PLANS.country_code.toLowerCase(),
    )
  ) {
    entries.push(premiumEuExpansion);
  }

  const trackerRemoval: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-tracker-removal-heading"),
    snippet: l10n.getString("whatsnew-feature-tracker-removal-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-tracker-removal-description-2",
        )}
        heading={l10n.getString("whatsnew-feature-tracker-removal-heading")}
        image={TrackerRemovalHero}
      />
    ),
    icon: TrackerRemovalIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_tracker-removal_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2022,
      month: 8,
      day: 16,
    },
  };
  // Only show its announcement if tracker removal is live:
  if (isFlagActive(props.runtimeData, "tracker_removal")) {
    entries.push(trackerRemoval);
  }

  const phoneAnnouncement: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-phone-header"),
    snippet: l10n.getString("whatsnew-feature-phone-snippet"),
    content:
      props.runtimeData && isPhonesAvailableInCountry(props.runtimeData) ? (
        <WhatsNewContent
          description={l10n.getString("whatsnew-feature-phone-description")}
          heading={l10n.getString("whatsnew-feature-phone-header")}
          image={PhoneMaskingHero}
          videos={{
            // Unfortunately video files cannot currently be imported, so make
            // sure these files are present in /public. See
            // https://github.com/vercel/next.js/issues/35248
            "video/webm; codecs='vp9'":
              "/animations/whatsnew/phone-masking-hero.webm",
            "video/mp4": "/animations/whatsnew/phone-masking-hero.mp4",
          }}
          cta={
            <CtaLinkButton
              subscribed={props.profile.has_phone}
              label={l10n.getString("whatsnew-feature-phone-upgrade-cta")}
            />
          }
        />
      ) : null,

    icon: PhoneMaskingIcon,
    dismissal: useLocalDismissal(`whatsnew-feature_phone_${props.profile.id}`),
    announcementDate: {
      year: 2022,
      month: 10,
      day: 11,
    },
  };

  // Only show its announcement if phone masking is live:
  if (isPhonesAvailableInCountry(props.runtimeData)) {
    entries.push(phoneAnnouncement);
  }

  const vpnAndRelayAnnouncement: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-bundle-header-2", {
      savings: "40%",
    }),
    snippet: l10n.getString("whatsnew-feature-bundle-snippet-2"),
    content:
      props.runtimeData && isBundleAvailableInCountry(props.runtimeData) ? (
        <WhatsNewContent
          description={l10n.getString("whatsnew-feature-bundle-body-v2", {
            monthly_price: getBundlePrice(props.runtimeData, l10n),
            savings: "40%",
          })}
          heading={l10n.getString("whatsnew-feature-bundle-header-2", {
            savings: "40%",
          })}
          image={BundleHero}
          videos={{
            // Unfortunately video files cannot currently be imported, so make
            // sure these files are present in /public. See
            // https://github.com/vercel/next.js/issues/35248
            "video/webm; codecs='vp9'":
              "/animations/whatsnew/bundle-promo-hero.webm",
            "video/mp4": "/animations/whatsnew/bundle-promo-hero.mp4",
          }}
          cta={
            <CtaLinkButton
              // TODO: Add has_bundle to profile data => subscribed={props.profile.has_bundle}
              label={l10n.getString("whatsnew-feature-bundle-upgrade-cta")}
            />
          }
        />
      ) : null,

    icon: BundleIcon,
    dismissal: useLocalDismissal(`whatsnew-feature_phone_${props.profile.id}`),
    announcementDate: {
      year: 2022,
      month: 10,
      day: 11,
    },
  };

  // Only show its announcement if bundle is live:
  if (isBundleAvailableInCountry(props.runtimeData)) {
    entries.push(vpnAndRelayAnnouncement);
  }

  const firefoxIntegrationAnnouncement: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-firefox-integration-heading"),
    snippet: l10n.getString("whatsnew-feature-firefox-integration-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-firefox-integration-description",
        )}
        heading={l10n.getString("whatsnew-feature-firefox-integration-heading")}
        image={FirefoxIntegrationHero}
      />
    ),
    icon: FirefoxIntegrationIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_firefox-integration_${props.profile.id}`,
    ),
    // Week after release of Firefox 111 (to ensure it was rolled out to everyone)
    announcementDate: {
      year: 2023,
      month: 3,
      day: 21,
    },
  };
  if (
    isFlagActive(props.runtimeData, "firefox_integration") &&
    isUsingFirefox()
  ) {
    entries.push(firefoxIntegrationAnnouncement);
  }

  const mailingListAnnouncement: WhatsNewEntry = {
    title: l10n.getString("whatsnew-feature-mailing-list-heading"),
    snippet: l10n.getString("whatsnew-feature-mailing-list-snippet"),
    content: (
      <WhatsNewContent
        description={l10n.getString(
          "whatsnew-feature-mailing-list-description",
        )}
        heading={l10n.getString("whatsnew-feature-mailing-list-heading")}
        image={MailingListHero}
        cta={
          <a
            className={styles.cta}
            href="https://www.mozilla.org/newsletter/security-and-privacy/"
            target="_blank"
          >
            {l10n.getString("whatsnew-feature-mailing-list-cta")}
          </a>
        }
      />
    ),
    icon: MailingListIcon,
    dismissal: useLocalDismissal(
      `whatsnew-feature_mailing-list_${props.profile.id}`,
    ),
    announcementDate: {
      year: 2023,
      month: 6,
      day: 3,
    },
  };

  if (isFlagActive(props.runtimeData, "mailing_list_announcement")) {
    entries.push(mailingListAnnouncement);
  }

  const megabundleDismissal = useLocalDismissal(
    `whatsnew-megabundle_${props.profile.id}`,
  );

  if (
    isMegabundleAvailableInCountry(props.runtimeData) &&
    props.profile.has_premium &&
    !props.profile.has_phone &&
    !props.profile.has_vpn &&
    !props.profile.has_megabundle
  ) {
    const isPremium = isPeriodicalPremiumAvailableInCountry(props.runtimeData);

    const snippet = l10n.getString(
      isPremium
        ? "whatsnew-megabundle-premium-snippet"
        : "whatsnew-megabundle-snippet",
      { monthly_price: getMegabundlePrice(props.runtimeData, l10n) },
    );

    const description = l10n.getString(
      isPremium
        ? "whatsnew-megabundle-premium-description"
        : "whatsnew-megabundle-description",
      { monthly_price: getMegabundlePrice(props.runtimeData, l10n) },
    );

    const ctaText = l10n.getString(
      isPremium ? "whatsnew-megabundle-premium-cta" : "whatsnew-megabundle-cta",
    );

    const megabundleEntry: WhatsNewEntry = {
      title: l10n.getString("whatsnew-megabundle-heading"),
      snippet,
      content: (
        <WhatsNewContent
          heading={l10n.getString("whatsnew-megabundle-heading")}
          description={description}
          image={ShieldHero}
          cta={
            <a
              className={styles.cta}
              href={getMegabundleSubscribeLink(props.runtimeData)}
              target="_blank"
            >
              {ctaText}
            </a>
          }
        />
      ),
      icon: ShieldIcon,
      dismissal: megabundleDismissal,
      announcementDate: {
        year: 2025,
        month: 6,
        day: 3,
      },
    };

    entries.push(megabundleEntry);
  }

  const entriesNotInFuture = entries.filter((entry) => {
    const entryDate = new Date(
      Date.UTC(
        entry.announcementDate.year,
        entry.announcementDate.month - 1,
        entry.announcementDate.day,
      ),
    );
    // Filter out entries that are in the future:
    return entryDate.getTime() <= Date.now();
  });
  entriesNotInFuture.sort(entriesDescByDateSorter);

  const newEntries = entriesNotInFuture.filter((entry) => {
    const entryDate = new Date(
      Date.UTC(
        entry.announcementDate.year,
        entry.announcementDate.month - 1,
        entry.announcementDate.day,
      ),
    );
    const ageInMilliSeconds = Date.now() - entryDate.getTime();
    // Automatically move entries to the archive after 30 days:
    const isExpired = ageInMilliSeconds > 30 * 24 * 60 * 60 * 1000;
    return !entry.dismissal.isDismissed && !isExpired;
  });

  const { triggerProps, overlayProps } = useOverlayTrigger(
    { type: "dialog" },
    triggerState,
    triggerRef,
  );

  const positionProps = useOverlayPosition({
    targetRef: triggerRef,
    overlayRef: overlayRef,
    placement: "bottom end",
    offset: 10,
    isOpen: triggerState.isOpen,
  }).overlayProps;
  const overlayBugWorkaround = useOverlayBugWorkaround(triggerState);

  const { buttonProps } = useButton(triggerProps, triggerRef);

  if (entriesNotInFuture.length === 0) {
    return null;
  }

  const pill =
    newEntries.length > 0 ? (
      <i
        aria-label={l10n.getString("whatsnew-counter-label", {
          count: newEntries.length,
        })}
        className={styles.pill}
        data-testid="whatsnew-pill"
      >
        {newEntries.length}
      </i>
    ) : null;

  return (
    <>
      {overlayBugWorkaround}
      <button
        {...buttonProps}
        ref={triggerRef}
        data-testid="whatsnew-trigger"
        className={`${styles.trigger} ${
          triggerState.isOpen ? styles["is-open"] : ""
        } ${props.style}`}
      >
        <GiftIcon
          className={styles["trigger-icon"]}
          alt={l10n.getString("whatsnew-trigger-label")}
        />
        <span className={styles["trigger-label"]}>
          {l10n.getString("whatsnew-trigger-label")}
        </span>
        {pill}
      </button>
      {triggerState.isOpen && (
        <OverlayContainer>
          <WhatsNewPopover
            {...overlayProps}
            {...positionProps}
            ref={overlayRef}
            title={l10n.getString("whatsnew-trigger-label")}
            isOpen={triggerState.isOpen}
            onClose={() => triggerState.close()}
          >
            <WhatsNewDashboard
              new={newEntries}
              archive={entriesNotInFuture}
              onClose={() => triggerState.close()}
            />
          </WhatsNewPopover>
        </OverlayContainer>
      )}
    </>
  );
};

type PopoverProps = {
  title: string;
  children: ReactNode;
  isOpen: boolean;
  onClose: () => void;
} & HTMLAttributes<HTMLDivElement>;
const WhatsNewPopover = forwardRef<HTMLDivElement, PopoverProps>(
  ({ title, children, isOpen, onClose, ...otherProps }, ref) => {
    const { overlayProps } = useOverlay(
      {
        onClose: onClose,
        isOpen: isOpen,
        isDismissable: true,
      },
      ref as RefObject<HTMLDivElement>,
    );

    const { modalProps } = useModal();

    const { dialogProps, titleProps } = useDialog(
      {},
      ref as RefObject<HTMLDivElement>,
    );

    const mergedOverlayProps = mergeProps(
      overlayProps,
      dialogProps,
      otherProps,
      modalProps,
    );

    return (
      <FocusScope restoreFocus contain autoFocus>
        <div
          {...mergedOverlayProps}
          ref={ref}
          className={styles["popover-wrapper"]}
        >
          <VisuallyHidden>
            <h2 {...titleProps}>{title}</h2>
          </VisuallyHidden>
          {children}
          <DismissButton onDismiss={onClose} />
        </div>
      </FocusScope>
    );
  },
);
WhatsNewPopover.displayName = "WhatsNewPopover";

const entriesDescByDateSorter: Parameters<Array<WhatsNewEntry>["sort"]>[0] = (
  entryA,
  entryB,
) => {
  const dateANr =
    entryA.announcementDate.year +
    entryA.announcementDate.month / 100 +
    entryA.announcementDate.day / 10000;
  const dateBNr =
    entryB.announcementDate.year +
    entryB.announcementDate.month / 100 +
    entryB.announcementDate.day / 10000;

  return dateBNr - dateANr;
};
