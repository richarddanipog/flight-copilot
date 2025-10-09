export const toISO = (d: Date | undefined): string | undefined => {
  if (!d) return undefined;
  const y = d.getFullYear();
  const m = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${y}-${m}-${day}`;
};

export const classNames = (...c: (string | false | undefined)[]) => {
  return c.filter(Boolean).join(' ');
};
