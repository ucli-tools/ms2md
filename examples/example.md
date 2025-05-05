# Example Markdown Document with LaTeX Equations

This is an example Markdown document that demonstrates the format produced by MS2MD when converting from Word documents with mathematical content.

## Basic Formatting

MS2MD preserves basic formatting from Word documents:

- **Bold text** for emphasis
- *Italic text* for emphasis
- ~~Strikethrough text~~ for deleted content
- [Hyperlinks](https://github.com/yourusername/ms2md)

## Headings

Headings are converted to the appropriate Markdown level:

### Level 3 Heading
#### Level 4 Heading
##### Level 5 Heading

## Lists

Ordered and unordered lists are preserved:

1. First item
2. Second item
   1. Nested item 1
   2. Nested item 2
3. Third item

- Bullet point 1
- Bullet point 2
  - Nested bullet point
- Bullet point 3

## Tables

Tables are converted to Markdown pipe tables:

| **Name** | **Age** | **Occupation** |
|:---------|:--------|:---------------|
| John     | 30      | Engineer       |
| Jane     | 28      | Doctor         |
| Bob      | 35      | Teacher        |

## Images

Images are extracted and referenced properly:

![Example Image](images/example.png)

## Mathematical Equations

### Inline Equations

MS2MD converts inline equations from Word to LaTeX format. For example, the Pythagorean theorem: $a^2 + b^2 = c^2$ or Einstein's famous equation: $E = mc^2$.

### Display Equations

Display equations are centered on their own line:

$$
F = ma
$$

More complex equations are also supported:

$$
\int_{a}^{b} f(x) \, dx = F(b) - F(a)
$$

### Aligned Equations

Aligned equations maintain their alignment:

$$
\begin{aligned}
x &= y + z \\
y &= \frac{1}{2}z + 3 \\
z &= \sqrt{x^2 + y^2}
\end{aligned}
$$

### Matrices

Matrices are properly formatted:

$$
A = \begin{pmatrix}
1 & 2 & 3 \\
4 & 5 & 6 \\
7 & 8 & 9
\end{pmatrix}
$$

## Theorems and Proofs

**Theorem 1.** Let $f$ be a continuous function on $[a,b]$. Then $f$ is integrable on $[a,b]$.

*Proof.* Since $f$ is continuous on a closed interval $[a,b]$, it is bounded and the set of discontinuities has measure zero. Therefore, $f$ is Riemann integrable.

## Chemical Equations

Chemical equations are also supported:

$$
\ce{H2O + CO2 -> H2CO3}
$$

## Code Blocks

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Calculate the 10th Fibonacci number
result = fibonacci(10)
print(f"The 10th Fibonacci number is {result}")
```

## Footnotes

This sentence has a footnote[^1].

[^1]: This is the footnote content.

## Conclusion

This example demonstrates the capabilities of MS2MD for converting Word documents with mathematical content to Markdown with LaTeX equations.