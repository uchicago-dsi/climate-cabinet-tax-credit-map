import AutocompleteLogic from "@/components/AutocompleteLogic";
import Communities from "@/components/Communities";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import Locales from "@/components/Locales";

export default function Homepage() {
  return (
    <main className="w-full">
      <div className="w-full p-5">
        <Header />
      </div>
      <div className="w-full text-center justify-center">
        <h1>Clean Energy Tax Credit Bonus Eligibility Map</h1>
        <p className="py-5">
          Discover which Inflation Reduction Act (IRA) bonus territories fall in
          your jurisdiction to lower utility costs and maximize environmental
          impact.
        </p>
      </div>
      <div className="w-full text-center justify-center">
        <h2>Search Now</h2>
        <p className="py-5">
          Enter the name of a state, county, municipality, or rural electric
          cooperative to view its Justice 40 communities, energy communities,
          and designated low-income census tracts and MSAs on an interactive map
          and a description of available tax credit programs.
        </p>
        <AutocompleteLogic />
      </div>
      <div className="flex flex-row">
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
        <div className="flex justify-center border w-1/2 mx-20 my-5">
          <h4>Did you know?</h4>
        </div>
      </div>
      <div>
        <Communities />
      </div>
      <div>
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
      <div>
        <Locales />
      </div>
      <div className="flex flex-col justify-center border w-1/2 mx-20 my-5">
        <h4>Did you know?</h4>
        <p>
          There is a 30 percent base tax credit for clean energy projects that
          meet certain criteria, but project developers and utilities can push
          the value of these credits WAY higher--if they build in the right
          places.
        </p>
      </div>
      <div>
        <h5>Acknowledgements</h5>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Tristique
          et egestas quis ipsum suspendisse ultrices gravida. Ultricies integer
          quis auctor elit sed. Arcu bibendum at varius vel. Augue neque gravida
          in fermentum et sollicitudin ac orci. Egestas erat imperdiet sed
          euismod nisi porta lorem mollis aliquam. Enim nec dui nunc mattis enim
          ut. Amet justo donec enim diam vulputate ut. Velit laoreet id donec
          ultrices tincidunt arcu. Scelerisque purus semper eget duis. Dignissim
          enim sit amet venenatis urna cursus.{" "}
        </p>
        <h5>Have Questions?</h5>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Tristique
          et egestas quis ipsum suspendisse ultrices gravida. Ultricies integer
          quis auctor elit sed. Arcu bibendum at varius vel. Augue neque gravida
          in fermentum et sollicitudin ac orci. Egestas erat imperdiet sed
          euismod nisi porta lorem mollis aliquam. Enim nec dui nunc mattis enim
          ut. Amet justo donec enim diam vulputate ut. Velit laoreet id donec
          ultrices tincidunt arcu. Scelerisque purus semper eget duis. Dignissim
          enim sit amet venenatis urna cursus.{" "}
        </p>
      </div>
      <div>
        <Footer />
      </div>
    </main>
  );
}
