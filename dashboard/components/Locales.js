import Locale from "./Locale";

export default function Locales() {
  const localeData = [
    { name: "Locale1", description: "Description for Locale1" },
    { name: "Locale2", description: "Description for Locale2" },
    // ... more data
  ];

  return (
    <div>
      {localeData.map((locale, index) => (
        <Locale
          key={index}
          name={locale.name}
          description={locale.description}
        />
      ))}
    </div>
  );
}
