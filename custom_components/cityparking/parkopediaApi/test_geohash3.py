# 1) Confirm exact string contents (no hidden chars)
gh = "b6e4u151e1dvskech0"
print("repr:", repr(gh))
print("bytes:", gh.encode("utf-8"))

# 2) Confirm what file Python is importing for the library
import pygeohash as pgh
import importlib, sys
print("pygeohash file:", getattr(pgh, "__file__", "<builtin>"))
print("module search path (first 6):", sys.path[:6])

# 3) Quick known-good test geohash
# Known test: "u4pruydqqvj" -> ~57.64911, 10.40744 (common test example)
print("known test decode:", pgh.decode("u4pruydqqvj"))

# 4) pip package info (run in shell)
# pip show pygeohash
