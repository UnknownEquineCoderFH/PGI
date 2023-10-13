`:: Types`
   - **\<tag>**: A rule.
   - **int**: A natural number.
   - **/regex/**: A regex rule.
   - **"string"**: A string literal.
   - **bool**: either True or False.


`:: Operators`
   - **<**: Less than.
   - **\>**: Greater than.
   - **=**: Equals.
   - **<=**: Less than or equal.
   - **\>=**: Greater than or equal.
   - **!=**: Not equal.
   - **&**: Logical and.
   - **|**: Logical or.


`:: Builtins`
   - **length**(*\<tag>*) → *int*: Get the length of the tag.
   - **hash**(*\<tag>*) → *int*: Get the hash of the tag.
   - **as_int**(*\<tag>*) → *int*: Get the numerical value of the tag.
   - **matches**(*\<tag>*, */regex/*) → *bool*: Whether a certain tag matches the given regex.
   - **contains_any**(*\<tag>*, *"string"*) → *bool*: Whether a certain tag contains any character in the given string literal.
   - **contains_all**(*\<tag>*, *"string"*) → *bool*: Whether a certain tag contains all characters in the given string literal.
   - **sample**(*\<tag>*, *int*) → bool: Sample a random tag from the given tag.


`:: File Definition`

Each line of a constraints file would contain a Predicate over one or more tags.
Such constraints would be translated into python code, dynamically loaded and executed when expansions are generated.
Some examples include:

```
# Tag <id> must be at least 5 characters long.
length(<id>) >= 5

# Tag <id> must be at least 5 characters long and contain at least one digit.
length(<id>) >= 5 & contains_any(<id>, "0123456789")

# Tag <id> must be at least 5 characters long and contain at least one digit or one special character.
length(<id>) >= 5 & (contains_any(<id>, "0123456789") | contains_any(<id>, "!@#$%^&*()"))

# Tag <id> in <assignment> expression must start with a letter.
matches(<assignment>.<id>, /^[a-zA-Z]/)

# Tag <payload> must have length equal to the numerical value of tag <length>.
length(<payload>) = as_int(<length>)

# The above constraint, but it applies only to <payload> and <length> tags belonging to an <assignment> expression.
length(<assignment>.<payload>) = as_int(<assignment>.<length>)
```