/**
 * Utilities used throughout the application.
 */


/**
 * Makes a POST request and handles any errors that may occur.
 * 
 * @param {*} url - The URL to the resource.
 * @param {*} args - The request body.
 * @param {*} errMsg - A message to display if an error occurs.
 * @returns JSON object
 */
const post = async (url, args, errMsg) => {
    let r = await fetch(url, {
        cache: 'force-cache',
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(args),
    });
    if (!r.ok) {
        return {
            error: errMsg
        };
    }
    return await r.json();
}


/**
 * Makes a GET request and handles any errors that may occur.
 * @param {*} url - The URL to the resource.
 * @param {*} errMsg - A message to display if an error occurs.
 * @returns JSON object.
 */
const get = async (url, errMsg) => {
    let r = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    });
    if (!r.ok) {
        return {
            error: errMsg
        };
    };
    return await r.json();
}


/**
 * Provides a "debounce" function to prevent excessive numbers
 * of user requests from overwhelming API servers. The
 * timeout/delay defaults to 100 milliseconds. For reference, please see:
 * https://www.freecodecamp.org/news/javascript-debounce-example/
 * 
 * @param {*} func - The function to delay.
 * @param {*} timeout - The number of milliseconds to delay.
 * @returns 
 */
function debounce(func, timeout = 100){
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

export { debounce, get, post };