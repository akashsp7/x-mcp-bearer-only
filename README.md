# X API FastMCP Server

Run a local MCP server that exposes the X API OpenAPI spec as tools using
FastMCP. Streaming and webhook endpoints are excluded.

This repo now supports two useful modes:

- Bearer-token mode for public read-only access
- OAuth1 mode for user-context endpoints

For a strict read-only Codex setup, use the Bearer-token mode and the provided
read-only profile.

## Prerequisites

- Python 3.10+
- An X Developer Platform app
- Optional: an xAI API key if you want to run the Grok test client

## Recommended setup for strict read-only access

This is the safest profile for your use case. It exposes only a conservative
allowlist of GET-only tools and does not request write-capable OAuth consent.

1. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Create your local `.env` from the read-only template:
   - `cp .env.readonly.example .env`
3. In the X Developer Console, copy your app's Bearer token into:
   - `X_BEARER_TOKEN`
4. Smoke test the server over stdio:
   - `.venv/bin/python smoke_test.py`
   - Optional live lookup: `.venv/bin/python smoke_test.py --username x`
5. Install it into Codex as a stdio MCP server:
   - `codex mcp add x-mcp-readonly -- /Users/akash/Documents/WORK/x-mcp/run_codex_stdio.sh`
6. Confirm the configuration:
   - `codex mcp get x-mcp-readonly`

Notes:

- `X_READ_ONLY_ONLY=1` forces the server to expose only GET operations.
- The provided allowlist is intentionally conservative. It excludes DMs,
  bookmarks, likes, follows, mute/block actions, media upload, and all other
  write-capable endpoints.
- Some read endpoints on X still require user-context auth. Those are not part
  of the default read-only allowlist here.

## General setup (local)

1. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Create your local `.env`:
   - `cp env.example .env`
   - Choose an auth mode:
     - `X_AUTH_MODE=bearer` for public read-only access with `X_BEARER_TOKEN`
     - `X_AUTH_MODE=oauth1` for OAuth1 user-context access
     - `X_AUTH_MODE=auto` to prefer Bearer auth when available, otherwise OAuth1
   - Bearer mode:
     - `X_BEARER_TOKEN`
   - OAuth1 mode:
     - `X_OAUTH_CONSUMER_KEY`
     - `X_OAUTH_CONSUMER_SECRET`
   - OAuth1 callback (defaults are fine):
     - `X_OAUTH_CALLBACK_HOST` (default `127.0.0.1`)
     - `X_OAUTH_CALLBACK_PORT` (default `8976`)
     - `X_OAUTH_CALLBACK_PATH` (default `/oauth/callback`)
     - `X_OAUTH_CALLBACK_TIMEOUT` (default `300`)
   - Server settings (optional):
     - `X_API_BASE_URL` (default `https://api.x.com`)
     - `X_API_TIMEOUT` (default `30`)
     - `X_READ_ONLY_ONLY` (default `0`; when `1`, only GET tools are exposed)
     - `MCP_TRANSPORT` (default `http`; use `stdio` for Codex/desktop clients)
     - `MCP_HOST` (default `127.0.0.1`)
     - `MCP_PORT` (default `8000`)
     - `MCP_PATH` (default `/mcp`)
     - `X_API_DEBUG` (default `1`)
   - Tool filtering (optional, comma-separated):
     - `X_API_TOOL_ALLOWLIST`
     - `X_API_TOOL_DENYLIST`
   - Optional Grok test client:
     - `XAI_API_KEY`
     - `XAI_MODEL` (default `grok-4-1-fast`)
     - `MCP_SERVER_URL` (default `http://127.0.0.1:8000/mcp`)
   - Optional OAuth2 token generation:
     - `CLIENT_ID`
     - `CLIENT_SECRET`
     - `X_OAUTH_ACCESS_TOKEN`
     - `X_OAUTH_ACCESS_TOKEN_SECRET` (optional; required for static OAuth1 signing)
   - Optional OAuth1 debug output:
     - `X_OAUTH_PRINT_TOKENS`
     - `X_OAUTH_PRINT_AUTH_HEADER`
3. Register the callback URL in your X Developer App:

```
http://<X_OAUTH_CALLBACK_HOST>:<X_OAUTH_CALLBACK_PORT><X_OAUTH_CALLBACK_PATH>
```

Example (defaults):

```
http://127.0.0.1:8976/oauth/callback
```

4. Start the server:

```
python server.py
```

Default transport is HTTP, so the MCP endpoint is `http://127.0.0.1:8000/mcp`
unless you set `MCP_TRANSPORT=stdio` or pass `--transport stdio`.

5. Connect an MCP client:
- Local client: point it to `http://127.0.0.1:8000/mcp`.
- Remote client: tunnel your local server (e.g., ngrok) and use the public URL.

## Whitelisting tools

Use `X_API_TOOL_ALLOWLIST` to load a small, explicit set of tools:

```
X_API_TOOL_ALLOWLIST=getUsersByUsername,createPosts,searchPostsRecent
```

Whitelisting is applied at startup when the OpenAPI spec is loaded, so restart
the server after changes. See the full tool list below before building your
allowlist.

If `X_READ_ONLY_ONLY=1`, you must also set `X_API_TOOL_ALLOWLIST`. That mode is
intended for an explicit read-only surface, not "all GET endpoints".

## OAuth1 flow (startup behavior)

In `X_AUTH_MODE=oauth1`, the server will:

- use `X_OAUTH_ACCESS_TOKEN` and `X_OAUTH_ACCESS_TOKEN_SECRET` if both are set
- otherwise open a browser for OAuth1 consent and wait for the callback

Tokens obtained through the interactive OAuth1 flow are kept in memory only for
the lifetime of the server process. Set `X_OAUTH_PRINT_TOKENS=1` to print
tokens, or `X_OAUTH_PRINT_AUTH_HEADER=1` to print request headers.

## Available tool calls (allowlist-ready)

Below is the full list of tool calls you can whitelist via
`X_API_TOOL_ALLOWLIST`. Copy any of these into your `.env` allowlist.

- `addListsMember`
- `addUserPublicKey`
- `appendMediaUpload`
- `blockUsersDms`
- `createCommunityNotes`
- `createComplianceJobs`
- `createDirectMessagesByConversationId`
- `createDirectMessagesByParticipantId`
- `createDirectMessagesConversation`
- `createLists`
- `createMediaMetadata`
- `createMediaSubtitles`
- `createPosts`
- `createUsersBookmark`
- `deleteActivitySubscription`
- `deleteAllConnections`
- `deleteCommunityNotes`
- `deleteConnectionsByEndpoint`
- `deleteConnectionsByUuids`
- `deleteDirectMessagesEvents`
- `deleteLists`
- `deleteMediaSubtitles`
- `deletePosts`
- `deleteUsersBookmark`
- `evaluateCommunityNotes`
- `finalizeMediaUpload`
- `followList`
- `followUser`
- `getAccountActivitySubscriptionCount`
- `getActivitySubscriptions`
- `getChatConversation`
- `getChatConversations`
- `getCommunitiesById`
- `getComplianceJobs`
- `getComplianceJobsById`
- `getConnectionHistory`
- `getDirectMessagesEvents`
- `getDirectMessagesEventsByConversationId`
- `getDirectMessagesEventsById`
- `getDirectMessagesEventsByParticipantId`
- `getInsights28Hr`
- `getInsightsHistorical`
- `getListsById`
- `getListsFollowers`
- `getListsMembers`
- `getListsPosts`
- `getMarketplaceHandleAvailability`
- `getMediaAnalytics`
- `getMediaByMediaKey`
- `getMediaByMediaKeys`
- `getMediaUploadStatus`
- `getNews`
- `getOpenApiSpec`
- `getPostsAnalytics`
- `getPostsById`
- `getPostsByIds`
- `getPostsCountsAll`
- `getPostsCountsRecent`
- `getPostsLikingUsers`
- `getPostsQuotedPosts`
- `getPostsRepostedBy`
- `getPostsReposts`
- `getSpacesBuyers`
- `getSpacesByCreatorIds`
- `getSpacesById`
- `getSpacesByIds`
- `getSpacesPosts`
- `getTrendsByWoeid`
- `getTrendsPersonalizedTrends`
- `getUsage`
- `getUserPublicKeys`
- `getUsersAffiliates`
- `getUsersBlocking`
- `getUsersBookmarkFolders`
- `getUsersBookmarks`
- `getUsersBookmarksByFolderId`
- `getUsersById`
- `getUsersByIds`
- `getUsersByUsername`
- `getUsersByUsernames`
- `getUsersFollowedLists`
- `getUsersFollowers`
- `getUsersFollowing`
- `getUsersLikedPosts`
- `getUsersListMemberships`
- `getUsersMe`
- `getUsersMentions`
- `getUsersMuting`
- `getUsersOwnedLists`
- `getUsersPinnedLists`
- `getUsersPosts`
- `getUsersRepostsOfMe`
- `getUsersTimeline`
- `hidePostsReply`
- `initializeMediaUpload`
- `likePost`
- `mediaUpload`
- `muteUser`
- `pinList`
- `removeListsMemberByUserId`
- `repostPost`
- `searchCommunities`
- `searchCommunityNotesWritten`
- `searchEligiblePosts`
- `searchNews`
- `searchPostsAll`
- `searchPostsRecent`
- `searchSpaces`
- `searchUsers`
- `sendChatMessage`
- `unblockUsersDms`
- `unfollowList`
- `unfollowUser`
- `unlikePost`
- `unmuteUser`
- `unpinList`
- `unrepostPost`
- `updateActivitySubscription`
- `updateLists`

## Generate an OAuth2 user token (optional)

1. Add `CLIENT_ID` and `CLIENT_SECRET` to your `.env`.
2. Generate a user token with your preferred OAuth2 Authorization Code + PKCE
   flow.
3. Copy the access token into `.env` as `X_OAUTH_ACCESS_TOKEN`.
4. If you are using OAuth1 static signing instead, also set
   `X_OAUTH_ACCESS_TOKEN_SECRET`.

## Run the Grok MCP test client (optional)

1. Set `XAI_API_KEY` in `.env`.
2. Make sure your MCP server is running locally (or set `MCP_SERVER_URL`).
3. If Grok is not running on your machine, use ngrok to expose your local MCP
   server and set `MCP_SERVER_URL` to the public HTTPS URL that ends with `/mcp`.
   Example flow: `ngrok http 8000` then `MCP_SERVER_URL=https://<id>.ngrok-free.dev/mcp`.
4. Run `python test_grok_mcp.py`.

## Notes

- Endpoints with `/stream` or `/webhooks` in the path are excluded.
- Operations tagged `Stream` or `Webhooks`, or marked with
  `x-twitter-streaming: true`, are excluded.
- The OpenAPI spec is fetched from `https://api.twitter.com/2/openapi.json` at
  startup.
