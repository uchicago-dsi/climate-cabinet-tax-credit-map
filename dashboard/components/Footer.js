"use client";
import Image from "next/image";

export default function Footer() {
  return (
    <footer className="text-center">
      <div className="mx-auto w-[250px]">
        <Image
          src="/images/climate-cabinet-education-black.png"
          alt="Description"
          width={424} // width of the original image
          height={276} // height of the original image
        />
      </div>
      <div className="border-b border-ccgray-light">
        <p className=" w-2/3 mx-auto py-5">
          We identify and support local climate leaders
        </p>
      </div>
    </footer>
  );
}
