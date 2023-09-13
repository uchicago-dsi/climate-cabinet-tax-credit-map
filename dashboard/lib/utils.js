/**
 * General utilities used throughout the application.
 */


/**
 * Creates a proxied version of the instance that 
 * is bound to the instance's current "this" context.
 * 
 * Credit: https://github.com/pmndrs/valtio/discussions/466
 * 
 * @param {*} instance 
 * @returns The proxied instance.
 */
function bind(instance) {
    const obj = instance;
    const names = Object.getOwnPropertyNames(Object.getPrototypeOf(obj));
  
    for (const name of names) {
      const method = obj[name];
      if (name === "constructor" || typeof method !== "function") continue;
      obj[name] = (...args) => method.apply(instance, args);
    }
  
    return instance;
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

export { bind, debounce };