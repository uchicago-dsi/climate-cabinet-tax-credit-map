import Image from "next/image";

export default function Locale({ name, description, location }) {
  return (
    <div className="flex flex-row">
      <div className="w-1/2">
        <h5>{name}</h5>
        <p>{description}</p>
      </div>
      <div className="flex w-1/2 justify-end">
        <div className="w-3/4">
          <Image
            src="/images/locale-placeholder.png"
            alt="locale"
            width={696} // width of the original image
            height={500} // height of the original image
          />
        </div>
      </div>
    </div>
  );
}
