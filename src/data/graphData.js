export const graphNodes = [
  {
    id: "USER_882",
    label: "USER_882",
    badge: "FLAGGED",
    badgeColor: "crimson",
    type: "User",
    color: "#FF334B",
    glowColor: "rgba(255, 51, 75, 0.6)",
    icon: "User",
    x: 35,
    y: 42,
    risk: 0.96,
    status: "Flagged Syndicate Mule",
    details: {
      entityType: "User Account",
      ipAddress: "192.168.1.23",
      macAddress: "4A:2B:CC:90:E1",
      accountAge: "14 Days",
      kycTier: "Tier 1 (Basic)",
      flaggedCount: 4,
      totalVolume: "$74,200 USD",
      notes: "Known member of eastern European money laundering ring #88"
    }
  },
  {
    id: "DEVICE_99",
    label: "DEVICE_99",
    sublabel: "(Shared IP)",
    type: "Device",
    color: "#00E5FF",
    glowColor: "rgba(0, 229, 255, 0.6)",
    icon: "Laptop",
    x: 58,
    y: 33,
    risk: 0.91,
    status: "Shared Spoofed Hardware",
    details: {
      entityType: "Hardware / Device Fingerprint",
      ipAddress: "192.168.1.23 (Tor Exit / Datacenter Relay)",
      macAddress: "4A:2B:CC:90:E1",
      fingerprint: "FP-WIN11-CHROME-9981A",
      concurrentUsers: 2,
      location: "Frankfurt, Germany (Geo-Spoofed)",
      notes: "Device concurrently accessed by USER_882 and USER_101 within 4 minutes"
    }
  },
  {
    id: "USER_101",
    label: "USER_101",
    badge: "TARGET",
    badgeColor: "emerald",
    type: "User",
    color: "#00FF88",
    glowColor: "rgba(0, 255, 136, 0.6)",
    icon: "User",
    x: 64,
    y: 54,
    risk: 0.94,
    status: "Target Compromised Account",
    details: {
      entityType: "Target User Account",
      ipAddress: "192.168.1.23 (Shared via DEVICE_99)",
      recentTransaction: "$15,000.00 USD",
      originatorBank: "Metro Atlantic Credit Union",
      accountCreated: "2 Years Ago (Clean History)",
      compromiseIndicator: "Velocity spike + out-of-pattern crypto/wallet routing",
      notes: "Target victim whose credentials were stolen in credential-stuffing wave"
    }
  },
  {
    id: "WALLET_X7",
    label: "WALLET_X7",
    sublabel: "($15k)",
    type: "Wallet",
    color: "#FF9900",
    glowColor: "rgba(255, 153, 0, 0.6)",
    icon: "Wallet",
    x: 24,
    y: 56,
    risk: 0.88,
    status: "High-Velocity Crypto Destination",
    details: {
      entityType: "Custodial / Web3 Wallet",
      walletAddress: "0x7Fa8...9B14c0",
      chain: "Ethereum / Layer-2 Arbitrum",
      currentBalance: "$15,000.00 USD",
      inflowCount24h: 7,
      mixerAffiliation: "Tornado Cash associated hop",
      notes: "First-stage liquidation pool for syndicated transfers"
    }
  },
  {
    id: "TXN_4452",
    label: "TXN_4452",
    sublabel: "(3 hops)",
    type: "Transaction",
    color: "#A855F7",
    glowColor: "rgba(168, 85, 247, 0.6)",
    icon: "Receipt",
    x: 41,
    y: 62,
    risk: 0.92,
    status: "Rapid Circular Clearing Node",
    details: {
      entityType: "Intermediate Settlement Transaction",
      txnId: "TXN-2026-4452-981",
      amount: "$15,000.00 USD",
      latencyBetweenHops: "1.4 seconds (Scripted Automation)",
      routingProtocol: "Automated ACH / Wire Bridge",
      notes: "Automated layering transaction moving funds back toward originator syndicate"
    }
  }
];

export const graphEdges = [
  {
    id: "edge-user882-wallet",
    from: "USER_882",
    to: "WALLET_X7",
    color: "#FF9900",
    style: "dashed",
    label: "Transfer $15k",
    type: "Transfer"
  },
  {
    id: "edge-user882-txn",
    from: "USER_882",
    to: "TXN_4452",
    color: "#A855F7",
    style: "dashed",
    label: "3 hops",
    type: "Transfer"
  },
  {
    id: "edge-device-user882",
    from: "DEVICE_99",
    to: "USER_882",
    color: "#00E5FF",
    style: "dashed",
    label: "Shared IP",
    type: "Connection"
  },
  {
    id: "edge-device-user101",
    from: "DEVICE_99",
    to: "USER_101",
    color: "#00E5FF",
    style: "dashed",
    label: "Shared Device",
    type: "Connection"
  }
];

export const circularLoopBadge = {
  text: "3-HOP LOOP",
  subtext: "($15k)",
  color: "#FF334B",
  x: 73,
  y: 40
};
