# Contents #



# Introduction #

**Codebook** is the new name for what used to be called the ontology. A codebook is a (optionally hierarchical) collection of codes. Codebooks are attached to projects and can be very small (e.g. the possible values national/provincial/municipal in a dropdown) or much larger (e.g. all possible subjects in a NET coding scheme). Finally, codebooks can be based on other codebooks, 'inheriting' their codes and hierarchy.



# Concepts #

  * `code`: A code represents an object or concept that can be used in automatic or manual coding.
  * `label`: A code can have zero or more labels representing human readable labels in different languages and/or (computer readable) terms such as search queries or politician names.
  * `codebook`: A codebook is a set of codes that are available for coding. Every code in a codebook can also have a parent, defining a hierarchy of codes. A codebook is attached to a project, and admins of that project can edit the codebook.
  * `base`: A codebook can be based on one or more other codebooks. All codes in the base codebooks are inherited by the derived codebook.
  * `hiding`: A codebook can also hide a code from the base codebooks.


# Hierarchy #

From an external perspective, a codebook is characterised by two things: membership (which codes are part of the codebook) and hierarchy (which codes are children of which other codes). Every codebook can be seen as a (multi)tree of codes. This tree is based on a codebooks own codes and parent, the hierarchy of the bases of this codebook, and codes hidden by this codebook.

## Simple codebooks ##

A simple codebook is nothing more than a set of codes with optional parents. Membership is determined solely by this set, and the hierarchy is formed by the list of parents.

## Codebooks based on another codebook ##

If a codebook 'Child' is based on another codebook 'Parent', the membership is formed by the union of all members of Child and Parent minus any codes hidden by the Child.

Note that this definition is recursive, so the 'Parent' codebook is evaluated in the same was, recursively involving the base(s) of Parent as applicable.

## Codebooks based on more than one codebook ##

A codebook can have more than one base codebook. In that case, the first base that contains a code is 'leading'.

## Decision procedure ##

To determine the state of a code in a codebook, the following procedure is applied:

  1. If the codebook hides this code, it is not a member of this codebook.
  1. If the codebook contains the code, it is a member with the parent as defined in this codebook
  1. For each base codebook "from left to right":
> > + If the base codebook contains the code, it is a member of the current codebook with the parent as defined in this base

# Example #

Suppose that we have a codebook `issues` like this


| <p align='center'>Codebook <b>issues</b></p> | | |
|:---------------------------------------------|:|:|
| **Code** | **Parent** | **Hide** |
| Issues |  |  |
| Environment | Issues |  |
| National Parks | Environment |  |
| Infrastructure | Issues |  |
| Roads | Infrastructure |  |
| Public transport | Infrastructure |  |

This codebook yields a hierarchy that can be visualised as:

  * **issues**
    * Issues
      * Environment
        * National parks
      * Infrastructure
        * Roads
        * Public transport

## Example extension: adding a sub code ##

Now we want to extend this codebook by adding `rails` as a category under `Public transport`. The way to to this is to define a codebook `issuedetails` based on the codebook, adding that code with parent Public Transport. Note that the new codebook does not /contain/ public transport, but only uses it as a parent:

| <p align='center'>Codebook <b>issuedetails</b> <i>based on</i> Issues</p> | | |
|:--------------------------------------------------------------------------|:|:|
| **Code** | **Parent** | **Hide** |
| Rails | Public Transport |  |

This yields the following 'composite' codebook, using <font color='gray'>a gray font</font> for the inherited definitions

  * **issuedetails**
    * <font color='gray'>Issues</font>
      * <font color='gray'>Environment</font>
        * <font color='gray'>National parks</font>
      * <font color='gray'>Infrastructure</font>
        * <font color='gray'>Roads</font>
        * <font color='gray'>Public transport</font>
          * Rails

So, _Rails_ is placed under _Public Transport_ because of the definition in this codebook. _Public Transport_ is placed under _Issues_ because that is where the base codebook _issues_ places it.

## Example extension: Moving a code ##

Now let us suppose that we decide that for another project we specify public transport as an environmental issue rather than an infrastructure issue. This can be done by redefining the parent:

| <p align='center'>Codebook <b>issuemoved</b> <i>based on</i> Issuedetails</p> | | |
|:------------------------------------------------------------------------------|:|:|
| **Code** | **Parent** | **Hide** |
| Public Transport | Environment |  |

Yielding:

  * **issuemoved**
    * <font color='gray'>Issues</font>
      * <font color='gray'>Environment</font>
        * <font color='gray'>National parks</font>
        * Public transport
          * <font color='gray'>Rails</font>
      * <font color='gray'>Infrastructure</font>
        * <font color='gray'>Roads</font>

## Example extension: Hiding a code ##

Now suppose that in a new project we want to use the `issuemoved` codebook, but without the national parks code. This can be done with this definition:


| <p align='center'>Codebook <b>issuehide</b> <i>based on</i> Issuemoved</p> | | |
|:---------------------------------------------------------------------------|:|:|
| **Code** | **Parent** | **Hide** |
| National Parks |  | Yes |

Yielding the hierarchy:

  * **issuehide**
    * <font color='gray'>Issues</font>
      * <font color='gray'>Environment</font>
        * ~~National parks~~
        * <font color='gray'>Public transport</font>
          * <font color='gray'>Rails</font>
      * <font color='gray'>Infrastructure</font>
        * <font color='gray'>Roads</font>

(Using ~~strike through~~ to indicate that _National Parks_ is no longer included in this codebook)

## Example extension: Combining codebooks ##

Now let's assume that we want to create a codebook with both actors and issues. The best way to do this is to create a standalone _Actors_ codebook, and then create a combined codebook:


| <p align='center'>Codebook <b>actors</b></p> | | |
|:---------------------------------------------|:|:|
| **Code** | **Parent** | **Hide** |
| Actors |  |  |
| Government | Actors |  |
| Citizens   | Actors |  |

  * **actors**
    * Actors
      * Government
      * Citizens

Which can then be combined with our _issuehide_ codebook:

| <p align='center'>Codebook <b>combined</b> <i>based on</i> issuehide, actors </p> | | |
|:----------------------------------------------------------------------------------|:|:|

Yielding a (multitree) hierarchy:


  * **combined**
    * <font color='gray'>Actors</font>
      * <font color='gray'>Government</font>
      * <font color='gray'>Citizens</font>
    * <font color='gray'>Issues</font>
      * <font color='gray'>Environment</font>
        * <font color='gray'>Public transport</font>
          * <font color='gray'>Rails</font>
      * <font color='gray'>Infrastructure</font>
        * <font color='gray'>Roads</font>


## Final example: Conflicting bases ##

Now let's imagine that for some reason we define a _railactors_ codebook that includes _Public transport_ as part of the government:


| <p align='center'>Codebook <b>railactors</b> <i>based on</i> actors</p> | | |
|:------------------------------------------------------------------------|:|:|
| **Code** | **Parent** | **Hide** |
| Public transport | Government |  |

  * **railactors**
    * <font color='gray'>Actors</font>
      * <font color='gray'>Government </font>
        * Public transport
      * <font color='gray'>Citizens</font>

Now, if we combine railactors with issues, the parent for _Public transport_ is conflicting: is is _government_ or _environment_? Moreover, what happens with the _Rail_ child of _public transport_?

If actors is listed as base before issues, the parent is actors is leading, so _public transport_ will be categorised under _Government_. If it is the other way around, it will be placed under _Environment_. _Rails_ will always be placed under _Public Transport_ (as the only definition for _rails_ is in issues, and that is where it is placed there).


| <p align='center'>Codebook <b>actorissue</b> <i>based on</i> railactors, issuehide </p> | | |
|:----------------------------------------------------------------------------------------|:|:|

  * **actorissue**
    * <font color='gray'>Actors</font>
      * <font color='gray'>Government </font>
        * <font color='gray'><b>Public transport</b></font>
          * <font color='gray'><b>Rails</b></font>
      * <font color='gray'>Citizens</font>
    * <font color='gray'>Issues</font>
      * <font color='gray'>Environment</font>
      * <font color='gray'>Infrastructure</font>
        * <font color='gray'>Roads</font>

| <p align='center'>Codebook <b>issueactor</b> <i>based on</i> issuehide, railactors </p> | | |
|:----------------------------------------------------------------------------------------|:|:|


  * **issueactor**
    * <font color='gray'>Actors</font>
      * <font color='gray'>Government </font>
      * <font color='gray'>Citizens</font>
    * <font color='gray'>Issues</font>
      * <font color='gray'>Environment</font>
        * <font color='gray'><b>Public transport</b></font>
          * <font color='gray'><b>Rails</b></font>
      * <font color='gray'>Infrastructure</font>
        * <font color='gray'>Roads</font>

(We could also represent this by placing Issues above Actors in the hierarchy, but the order of children is not fixed by the definition, ie a user can decide how to sort the codebook)

# Cycles and Missing Links #

Codebooks should not contain cycles, either in the code definitions or in the bases. This cannot be checked by the database, so care should be taken not to introduce cycles as this may lead to infinite loops.

Additionally, it is possible to specify a code as parent that does not exist in the current codebook. This is useful if the code is contained in a base codebook, but difficult to interpret otherwise.

# Technical details #

In the database, the codebook tables are all named `code*`. In python/django, the model classes are contained in the modules `amcat.model.coding.code` and  `amcat.model.coding.codebook`.