/**
 * A formatted anchor tag.
 */


function Link({ url, text }) {
    return (
        <>
            <a 
                href={url}
                target="_blank"
                className="font-bold text-blue-600"
            >
                {text}
            </a>
        </>
       
    )
}

export default Link;