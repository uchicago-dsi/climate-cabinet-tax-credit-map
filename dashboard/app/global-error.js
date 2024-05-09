"use client";

export default function GlobalError({ error, reset }) {
  return (
    <html>
      <body>
        <div>
          <h2>Something went wrong!</h2>
          <p>Please contact the maintainers of this application.</p>
        </div>
      </body>
    </html>
  );
}
