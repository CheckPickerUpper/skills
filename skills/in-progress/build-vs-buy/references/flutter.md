# Flutter: usual owners to check

Candidates to check, not a verdict. The repository's declared choices and
`pubspec.yaml` come first; confirm current APIs and maintenance on pub.dev and
the package repository.

| Need | Usual owner |
| --- | --- |
| App state, dependency access, async loading, error and data state | `flutter_riverpod` |
| Routing, redirects, auth gates, deep links, nested sections | `go_router` |
| State variants, immutable models, `copyWith`, equality | `freezed` |
| JSON encoding and decoding of API types | `json_serializable` |
| Collection algorithms and deep equality | `collection` |
| Cancelable operations, stream groups, async memoization | `async` |
| API clients with auth headers, interceptors, cancellation, upload and download | `dio` |
| Tokens and other secrets | `flutter_secure_storage` |
| Simple non-sensitive preferences | `shared_preferences` |
| Structured offline data with typed reactive queries | `drift` (prefer it over raw `sqflite` unless low-level control is intended) |
| Dates, numbers, money, plurals and locale text | `intl` |
| Production time reads that tests can control | `clock` |
| Deterministic time in tests | `fake_async` |
| Logging | `logging` |
| Crash and error reporting | `sentry_flutter` |
| App version and build metadata | `package_info_plus` |
| App, cache, temporary and document directories | `path_provider` |
| Connection state (not proof the internet is reachable) | `connectivity_plus` |
| Opening URLs, mail, phone and SMS | `url_launcher` |
| Universal links, deep links, custom schemes | `app_links` |
| Runtime permissions | `permission_handler` |
| Remote images with placeholder, error and cache | `cached_network_image` |
| Caching other downloaded files | `flutter_cache_manager` |
| Camera or gallery picking | `image_picker` |
| Document and file picking | `file_picker` |
| Platform share sheets | `share_plus` |
| Device and OS metadata | `device_info_plus` |
| SVG rendering | `flutter_svg` |
| Lottie animations | `lottie` |
| Non-trivial form validation and state | `formz` |
| Local notifications | `flutter_local_notifications` |
| Biometric or passcode unlock | `local_auth` |
| Subscriptions and in-app purchases | `in_app_purchase` |
