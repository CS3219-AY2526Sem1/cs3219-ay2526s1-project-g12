/**
 * A utility type that makes all properties of a given type mutable (removes readonly modifiers).
 */
export type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};
