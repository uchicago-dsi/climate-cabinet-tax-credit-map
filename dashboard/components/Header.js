"use client";
import Image from "next/image";
import "./Header.css";

export default function Header() {
  return (
    <nav className="flex flex-row pb-2 pt-2">
      <div className="w-[200px]">
        <a href="https://www.climatecabinetaction.org/">
          <Image
            src="/images/climate-cabinet-education-black.png"
            alt="Climate Cabinet Education"
            width={424} // width of the original image
            height={276} // height of the original image
          />
        </a>
      </div>
      <div className="flex flex-1 items-center justify-end nav-menu">
        <nav>
          <ul className="flex">
            <li>
              <a href="https://www.climatecabinetaction.org/#Subscribe">
                Subscribe
              </a>
            </li>
            <li>
              <a href="https://secure.actblue.com/donate/ccaf">Donate</a>
            </li>
            <li>
              <a href="https://www.climatecabinetaction.org/">Home</a>
            </li>
          </ul>
        </nav>
      </div>
    </nav>
  );
}
