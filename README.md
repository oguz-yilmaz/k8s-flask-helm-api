# Namecheap Cloud DevOps Code Challenge

## The Challenge

Your challenge is to develop an API set that accept a string input or return a random one previously inserted.
The entire structure must run on a Kubernetes cluster.
To test your tool, you can use [KinD](https://kind.sigs.k8s.io/).

## Specifications

- API set should be exposed trough HTTP protocol.
- Persistence should be on MySQL.
- API set must contain two API:
  - SET API accepts a string value and persists it.
  - GET API returns one of the previously persisted string values (choose a random one).
- Any component must be containerized.
- Installation of the entire structure must be done with one or more Helm charts.
- A briefly INSTALLATION.md must be provided, we must be able to get the system going without direct support.

## Time allowed

People who have successfully passed the challenge and are now happy members of our Cloud DevOps team usually took an average of 1.5 hour to complete it.

### Some additional features that could be useful (optional)

- If you feel confident, you can also add other useful API to the set, it's up to you (remember we love KISS principle :-) ).
- A small documentation exposed on OpenAPI specifications can be a good idea
- Whatever you feel can be a good feature :-)

## Rules

- Core components must be developed using Python programming language (Flask is highly recommended too) or GoLang (GinGonic recommended in this case).
- Be sure API are not returning unhandled exceptions on edge cases.
- Let's use this repository issues and PR in an interactive way to discuss and improve the final result.

## Advice

- **Even if this API set is really simple, try to design and implement your solution as you would do for real production code**. Show us how you create clean, maintainable code. Build something that we'd be happy to contribute to. This is not a programming contest where dirty hacks win the game.
