# Scraper checklist #

This section presents an overview of the scrapers that need to be written (anew) for the new scraper framework.

Scraper status:
  * N = Does not exist
  * W = Works
  * B = Broken

| **Mediumtype**| **Medium** | **Old framework** | **New framework** | **Runs daily** |
|:--------------|:-----------|:------------------|:------------------|:---------------|
| **Newspapers** |  **National** |  |  |  |
|  | Top 5 - most read | N | W | N |
|  | Volkskrant | B (W till 26-01-12)| W | Y |
|  | De Telegraaf | W | W | Y |
|  | Trouw | B (W till 26-01-12) | W | Y |
|  | NRC Handelsblad | W | W | Y |
|  | Algemeen Dagblad | B (W till 21-01-12)| W | Y |
|  | NRC Next | N | N | N |
|  | **Regional**  |  |  |  |
|  | Dagblad vh Noorden | W |N |  |
|  | De Limburger | W | ? | N |
|  | Tubantia | ? | W | Y |
|  | Het Parool | ? | W | N |
|  | ... (add more) | N |N |  |
|  | **Free**  |  |  |  |
|  | Metro | B (W till 20-01-12) |W | Y |
|  | Spits | B (W till 20-01-12)| W | Y |
| **Internet** | **Newssites**  |  |  |  |
|  | Nu.nl | B (W by call?) | W | N |
|  | Nujij.nl | B (W by call?)| N |  |
|  | GeenStijl.nl | W (by call) | N |  |
|  | Foknieuws.nl | W (by call) | W | Y |
|  | NOS nieuws | ? | W | Y |
|  | RTL nieuws | ? | W | Y |
|  | **Social**  |  |  |  |
|  | Fok forum | ? | N |  |
|  | Twitter | N (W is obsolete) | N |  |
| **Television** | **TT888** |  |  |  |
|  | NOS | W | N |  |
|  | NOS Teletekst | N | W | Hourly |
| **Government** |  |  |  |  |
|  | Handelingen 2e kamer | ? | ? | ? |
|  | Kamervragen | ? | ? | ? |