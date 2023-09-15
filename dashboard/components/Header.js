"use client";
import Image from "next/image";
import "./Header.css";

export default function Header() {
  return (
    <div className="flex flex-row">
      <div className="flex flex-1 justify-start items-center">
        <a href="https://www.climatecabinetaction.org/">
          <Image
            src="/images/climate-cabinet-education-black.png"
            alt="Climate Cabinet Education"
            width={176} // width of the original image
            height={115} // height of the original image
          />
        </a>
      </div>
      <nav className="flex flex-6 items-center justify-center nav-menu font-bold text-base">
        <ul className="flex">
          <li>
            <a href="https://climatecabineteducation.org/">Home</a>
          </li>
          <li>
            <a href="https://climatecabineteducation.org/about-whoweare/">
              About Us
            </a>
          </li>
          <li>
            <a href="https://climatecabineteducation.org/policy_resources/">
              Policy Resources
            </a>
          </li>
          <li>
            <a href="https://climatecabineteducation.org/climate-bills/#">
              Data Science
            </a>
          </li>
          <li>
            <a href="https://climatecabineteducation.org/blog">Media</a>
          </li>
          <li>
            <a href="https://climatecabineteducation.org/contact-us/">
              Contact Us
            </a>
          </li>
        </ul>
      </nav>
      <div className="flex flex-1 justify-end items-center">
        <a
          className="btn cc-button rounded-full"
          href="https://secure.actblue.com/donate/ccaf"
        >
          DONATE NOW
        </a>
      </div>
    </div>
  );
}
