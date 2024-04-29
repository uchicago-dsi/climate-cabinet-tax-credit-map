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

export { bind };
