export function formatRelativeTime(value: string | null | undefined): string {
  if (!value) {
    return "just now";
  }

  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) {
    return "just now";
  }

  const deltaSeconds = Math.floor((Date.now() - timestamp) / 1000);
  if (deltaSeconds < 60) {
    return "just now";
  }
  if (deltaSeconds < 3600) {
    return `${Math.floor(deltaSeconds / 60)}m ago`;
  }
  if (deltaSeconds < 86400) {
    return `${Math.floor(deltaSeconds / 3600)}h ago`;
  }
  return `${Math.floor(deltaSeconds / 86400)}d ago`;
}
