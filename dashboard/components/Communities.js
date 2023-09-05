import Community from "./Community";

export default function Communities() {
  const communityData = [
    {
      name: "Justice 40 Communities",
      description: "Justice Justice Justice Justice Justice",
    },
    {
      name: "Low-Income Communities",
      description: "Low-Income Low-Income Low-Income Low-Income Low-Income",
    },
    {
      name: "Energy Communities",
      description: "Energy Energy Energy Energy Energy Energy",
    },
  ];

  return (
    <div>
      {communityData.map((community, index) => (
        <Community
          key={index}
          name={community.name}
          description={community.description}
        />
      ))}
    </div>
  );
}
