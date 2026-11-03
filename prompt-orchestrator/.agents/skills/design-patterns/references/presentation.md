# Presentation and UI Architecture

Load this when the force is about how UI state, user input and rendering are organised, on the
server, the web, mobile or desktop. Platform guidance at the end comes from the platform
owners' own documentation; follow it unless the codebase has already settled on something
else, in which case follow the codebase.

## The question every presentation pattern answers
Who owns the state, who may change it, and how does a change reach the screen? Name these three
for the screen in front of you before picking a pattern:

1. **Source of truth**: where the state lives (server, store, view model, component).
2. **Writers**: what may change it (only the owner through named actions, or anyone).
3. **Propagation**: how the view learns of a change (re-render from state, observation, manual
   update calls).

Unidirectional data flow (state flows down to the view, events flow up to the owner, the owner
produces new state) is the default on every current major UI platform listed below. Two-way
binding is a convenience at the input-field level, not an architecture.

## Pattern table

| Pattern | Shape | Fits | Do not use when | Lighter form |
|---------|-------|------|-----------------|--------------|
| MVC (server) | A controller handles a request, works with the model, picks a view to render | Server-rendered web apps; the default in Rails, Django, Laravel, Spring MVC, ASP.NET MVC | Rich client state lives in the browser | Framework controllers as they come; thin controllers, logic in the model or a service |
| MVC (classic desktop) | The view observes the model; the controller translates input into model changes | Historical desktop toolkits | A modern toolkit already prescribes something else | Follow the toolkit |
| MVP | A passive view exposes an interface; the presenter holds all presentation logic and drives the view | Toolkits whose views are hard to test (older Android views, WinForms, UIKit) | The toolkit renders declaratively from state | A plain presenter function returning a view model |
| MVVM | The view model exposes observable state and methods; the view renders the state and calls the methods | Android (ViewModel), Flutter, WPF and other binding toolkits | One screen with trivial state; a view model would only forward | State in the component or screen itself |
| MVI | Intents go to a reducer that produces one immutable state; side effects run outside the reducer | Screens with complex state machines, replay or time-travel needs | Simple screens: the ceremony outweighs the benefit | MVVM with a single immutable `uiState` and named actions |
| MVU (Elm architecture) | Model, view as a pure function of the model, update as a pure function of message and model | Elm, Redux-style stores, Bubble Tea, SwiftUI with a store, TCA | Teams unfamiliar with it on a small app | A reducer for the one complex screen |
| Flux / Redux | One store per app or feature; actions dispatched; reducers produce new state; views subscribe | Web apps with shared, cross-cutting client state | State is local to a component or comes from the server cache | Component state plus a server-cache library; React reducer plus context |
| VIPER | View, Interactor, Presenter, Entity, Router per module | Large UIKit codebases with strict module boundaries | SwiftUI apps or small teams | MVVM plus a coordinator for navigation |
| TCA (The Composable Architecture) | MVU for Swift with reducers, effects and scoped stores | SwiftUI apps that need composition and deterministic tests | The team cannot take the library dependency or learning cost | Observable models plus `@State` ownership |
| BLoC | Events in, states out through streams; widgets rebuild from state | Flutter apps already on the bloc package | New Flutter apps following the official guide (MVVM with commands) | ViewModel with ChangeNotifier |
| Coordinator / Router | Navigation decisions live outside screens | Deep links, reusable flows, UIKit navigation | One linear flow | The platform's declarative navigation state |
| Container / presentational | Containers fetch and own state; presentational components render props | Component libraries; testable visual components | Hooks already keep the split clear | Custom hooks for data, plain components for rendering |
| Server presentation (PoEAA) | Page controller, front controller, template view, transform view, two-step view, application controller | Server frameworks; every modern router is a front controller | Rarely worth hand-building | The framework's router and templates |
| Micro-frontends | Independently built and deployed UI slices composed at runtime or build time | Several teams shipping one product on separate cadences | One team: the integration cost buys nothing | Modules in one app with clear ownership |
| Islands / partial hydration | Static HTML with interactive islands hydrated on demand | Content-heavy sites with small interactive parts | App-like pages where most of the page is interactive | Server rendering plus progressive enhancement |

Look-alikes: MVP and MVVM differ in direction. A presenter calls the view; a view model is
observed by the view and never references it. MVI and MVU differ mostly in vocabulary; both put
one immutable state behind a reducer.

## Platform guidance

### Android (developer.android.com, architecture recommendations)
- Layers: a data layer with repositories (strongly recommended, even with a single data source)
  and a UI layer (strongly recommended); a domain layer with use cases only in big apps, to
  reuse logic across view models or to simplify one.
- UI layer: unidirectional data flow, where view models expose UI state through observation and
  receive actions through method calls (strongly recommended). Collect state with
  lifecycle-aware collection (`collectAsStateWithLifecycle`).
- Do not send one-off events from the view model to the UI; handle the event in the view model
  and express the result as state (strongly recommended).
- View models: screen level only, never in reusable components (use plain state holders there);
  no `Activity`, `Context` or `Resources` references; prefer `ViewModel` over
  `AndroidViewModel`; expose a single `uiState` as a `StateFlow`, built with `stateIn` and
  `WhileSubscribed(5000)` when it comes from streams.
- Coroutines and flows between layers; constructor dependency injection, Hilt in larger apps;
  single-activity apps with Compose for new UI.
- Testing: unit tests for view models (including flows) and the data layer, navigation tests,
  Macrobenchmark for startup; prefer fakes to mocks.

### iOS and SwiftUI (developer.apple.com, managing model data)
- Apply `@Observable` to model types; views track only the properties their body reads.
- The view or scene that creates the model stores it in `@State`; that is the source of truth.
  Share it through the environment or by passing it down; children bind with `@Bindable`.
- Apple's guidance has views work with observable models directly and does not prescribe a view
  model layer. Add one when a screen has logic worth testing apart from the view; otherwise keep
  logic in the model.
- UIKit codebases: MVVM or MVP with a coordinator for navigation are common; VIPER only for large
  modular codebases. TCA when the team accepts the dependency and wants reducer-based tests.

### Flutter (docs.flutter.dev, app architecture recommendations)
- Strongly recommended: separate data and UI layers, repositories in the data layer, views and
  view models in the UI layer (MVVM), no logic in widgets, unidirectional data flow, immutable
  data models, dependency injection, abstract repository classes, fakes for tests.
- Recommended: commands for user interaction events, generated immutable models, `go_router`.
- Conditional: a domain layer, separate API and domain models, `ChangeNotifier` for updates.

### React (react.dev, managing state)
- Model each visual state and derive the UI from it; avoid imperative DOM toggling.
- Keep state minimal: no redundant or derivable state; compute during render.
- Lift shared state to the closest common parent; use a `key` to reset state deliberately.
- Move complex update logic into a reducer; pass deep data with context; combine reducer and
  context to scale a feature. Server data belongs in a data-fetching or server-cache layer, not
  copied into client state.

### Server-rendered web (Rails, Django, Laravel, Spring MVC, ASP.NET Core MVC)
- Use the framework's front controller, routing and templates; do not rebuild them.
- Keep controllers thin: parse input, call one application operation, choose a response.
- Put domain logic in the model or a service layer (see `enterprise-and-ddd.md`); keep queries
  out of templates.

## Mobile-specific patterns
- **Single source of truth with offline-first**: the local database is the source the UI reads;
  the network refreshes it. Writes go to local storage first with a sync queue, with explicit
  conflict rules.
- **State restoration**: survive process death with saved state for what the user typed, not for
  data the repository can reload.
- **Background work**: use the platform scheduler (WorkManager, BGTaskScheduler) for deferrable
  work; never a long-running service or thread for it.
