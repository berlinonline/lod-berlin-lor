# Berlin's LOR structure ('Lebensweltlich Orientierte Räume') as Linked Open Data

The 'Lebensweltlich orientierten Räume', or LOR, is a system that divides the city of Berlin into a hierarchy of continuously smaller geographical units. 
At the top are the 12 Bezirke (burroughs).
The Bezirke are divided into 58 Prognoseräume, which are further divided into 143 Bezirksregionen.
Finally, at the lowest level, there are 542 Planungsräume.
The LORs are the basis for planning, prognosis and monitoring of demographic and social developments in Berlin. 

This dataset is a conversion of the existing WFS-services to Linked Data, or RDF.

The data is converted using a series of scripts and tools, all orchestrated by the [Makefile](Makefile).

It is then published as Linked Open Data using the [LOD Site Generator](https://github.com/berlinonline/lod-sg) repository as a template.

**[Start browsing the data!](https://berlinonline.github.io/lod-berlin-lor/)**

## License

All code in this repository is published under the [MIT License](License). All data (in particular [void.ttl](void.ttl) and [data/target/lors.ttl](data/static/berlinonline.ttl)) are published under [CC0](https://creativecommons.org/publicdomain/zero/1.0/).