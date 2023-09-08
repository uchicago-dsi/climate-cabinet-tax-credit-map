"use client";
import Image from "next/image";
import "./Header.css";

export default function Header() {
  return (
    <nav className="flex flex-row">
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
            <li>
              <a
                className="btn cc-button"
                href="https://secure.actblue.com/donate/ccaf"
              >
                Donate
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </nav>
  );
}
