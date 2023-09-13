"use client";
/***
 * The landing page for the site.
 */

// TODO: This doesn't work?
import "@/app/globals.css";
import 'mapbox-gl/dist/mapbox-gl.css';

import Autocomplete from "@/components/Autocomplete";
import Communities from "@/components/Communities";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import Locales from "@/components/Locales";
import Image from "next/image";


export default async function Home() {
  return (
    <main className="w-full">
      <div className="w-full px-10">
      </div>
      <div className="py-5 bg-ccgray-light">
        <div className="w-full text-center justify-center px-10">
          <h1>Clean Energy Tax Credit Bonus Eligibility Map</h1>
          <p className="py-5">
            Discover which Inflation Reduction Act (IRA) bonus territories fall
            in your jurisdiction to lower utility costs and maximize
            environmental impact.
          </p>
        </div>
        <div className="flex w-full text-center justify-center px-10">
          <div className="w-2/3">
            <h2>Search Now</h2>
            <p>
              Enter the name of a state, county, municipality, or rural electric
              cooperative to view its Justice 40 communities, energy
              communities, and designated low-income census tracts and MSAs on
              an interactive map and a description of available tax credit
              programs.
            </p>
            <form className="flex flex-row">
              <Autocomplete />
              <button className="cc-button mx-2">Submit</button>
            </form>
            <div>
          </div>
          </div>
        </div>
      </div>
      <div className="flex justify-center">
        <Image
          src="/images/map-placeholder.png"
          alt="locale"
          width={1378} // width of the original image
          height={816} // height of the original image
        />{" "}
      </div>
      <div className="flex flex-row px-10 py-10">
        <div className="w-1/2">
          <h4>
            The Inflation Reduction Act (IRA), signed into law on August 16,
            2022, is the biggest federal investment in climate in the United
            States’ history.
          </h4>
          <p>
            The legislation pledges an estimated $369 billion for clean energy
            and climate projects over the next 10 years, two-thirds of which
            will be distributed through clean energy tax credits.
          </p>
          <p>
            For the first time, public utility companies can access these tax
            credits directly to save money rather than going through a tax
            equity partner as a middleman. Furthermore, they can significantly
            boost their tax credit value by investing in certain geographic
            areas:
          </p>
        </div>
        <div className="flex w-1/2 border mx-20 my-5">
          <div className="flex flex-col w-full text-center">
            <h4>Did you know?</h4>
            <p>2/3</p>
            <p>
              of the total funding within the IRA will be delivered via clean
              energy tax credits
            </p>
          </div>
        </div>
      </div>
      <div className="flex w-full justify-center">
        <div className="w-3/4">
          <Communities />
        </div>
      </div>
      <div className="flex px-10">
        <p>
          However, to date, no one has mapped these key communities and their
          overlap for cooperative or municipal leaders, forcing them to rely on
          guesswork to make big investment decisions. To close this gap and
          reduce barriers to equitable IRA implementation, Climate Cabinet
          launched the tool for public use in 2023. Lorem ipsum dolor sit amet,
          consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
          labore et dolore magna aliqua. Tristique et egestas quis ipsum
          suspendisse ultrices gravida. Ultricies integer quis auctor elit sed.
          Arcu bibendum at varius vel. Augue neque gravida in fermentum et
          sollicitudin ac orci. Egestas erat imperdiet sed euismod nisi porta
          lorem mollis aliquam. Enim nec dui nunc mattis enim ut. Amet justo
          donec enim diam vulputate ut. Velit laoreet id donec ultrices
          tincidunt arcu. Scelerisque purus semper eget duis. Dignissim enim sit
          amet venenatis urna cursus.{" "}
        </p>
      </div>
      <div className="flex flex-col w-full px-10">
        <div className="flex w-full justify-end">
          <h3>Locale Spotlight</h3>
        </div>
        <div>
          <Locales />
        </div>
      </div>
      <div className="flex w-full justify-center">
        <div className="flex flex-col text-center border w-1/2 mx-20 my-5 p-5">
          <h4>Did you know?</h4>
          <p>
            There is a 30 percent base tax credit for clean energy projects that
            meet certain criteria, but project developers and utilities can push
            the value of these credits WAY higher--if they build in the right
            places.
          </p>
        </div>
      </div>
      <div className="px-10 py-5">
        <h5>Acknowledgements</h5>
        <p>
          <b>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua.
          </b>{" "}
          Tristique et egestas quis ipsum suspendisse ultrices gravida.
          Ultricies integer quis auctor elit sed. Arcu bibendum at varius vel.
          Augue neque gravida in fermentum et sollicitudin ac orci. Egestas erat
          imperdiet sed euismod nisi porta lorem mollis aliquam. Enim nec dui
          nunc mattis enim ut. Amet justo donec enim diam vulputate ut. Velit
          laoreet id donec ultrices tincidunt arcu. Scelerisque purus semper
          eget duis. Dignissim enim sit amet venenatis urna cursus.{" "}
        </p>
        <h5>Have Questions?</h5>
        <p>
          <b>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua.
          </b>{" "}
          Tristique et egestas quis ipsum suspendisse ultrices gravida.
          Ultricies integer quis auctor elit sed. Arcu bibendum at varius vel.
          Augue neque gravida in fermentum et sollicitudin ac orci. Egestas erat
          imperdiet sed euismod nisi porta lorem mollis aliquam. Enim nec dui
          nunc mattis enim ut. Amet justo donec enim diam vulputate ut. Velit
          laoreet id donec ultrices tincidunt arcu. Scelerisque purus semper
          eget duis. Dignissim enim sit amet venenatis urna cursus.{" "}
        </p>
      </div>
      <div>
      </div>
    </main>
  );
}

