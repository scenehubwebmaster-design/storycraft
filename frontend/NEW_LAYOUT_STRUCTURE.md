// NEW LAYOUT STRUCTURE TO REPLACE IN DMChat.jsx

return (
<Box
sx={{
        display: "flex",
        height: "100vh",
        overflow: "hidden",
        bgcolor: "background.default",
      }} >
{/_ LEFT: Settings Panel _/}
<LeftSettingsPanel
provider={provider}
setProvider={setProvider}
model={model}
setModel={setModel}
availableModels={availableModels}
selectedSession={selectedSession}
updateSessionSettings={updateSessionSettings}
ttsEnabled={ttsEnabled}
setTtsEnabled={setTtsEnabled}
ttsAutoPlay={ttsAutoPlay}
setTtsAutoPlay={setTtsAutoPlay}
ttsVoice={ttsVoice}
setTtsVoice={setTtsVoice}
ttsFlavorTextOnly={ttsFlavorTextOnly}
setTtsFlavorTextOnly={setTtsFlavorTextOnly}
sceneImageAutoGenerate={sceneImageAutoGenerate}
setSceneImageAutoGenerate={setSceneImageAutoGenerate}
activeCampaign={activeCampaign}
handleCampaignUpdate={handleCampaignUpdate}
collapsed={leftPanelCollapsed}
onToggleCollapse={() => setLeftPanelCollapsed(!leftPanelCollapsed)}
/>

      {/* CENTER-LEFT: Session List (toggle-able) */}
      <Drawer
        variant={isLargeScreen ? "persistent" : "temporary"}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            bgcolor: "background.paper",
            height: "100vh",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          },
        }}
      >
        {/* Session list header and content... (keep existing) */}
      </Drawer>

      {/* CENTER: Main Chat Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          overflow: "hidden",
          transition: theme.transitions.create(["margin"], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          marginLeft: drawerOpen && isLargeScreen ? 0 : `-${drawerWidth.lg}px`,
        }}
      >
        {/* Existing main chat content... */}
      </Box>

      {/* RIGHT: Party/Combat Panel */}
      {activeCampaign && rightPanelOpen && (
        <Box
          sx={{
            width: { xs: "100%", md: 360, lg: 380 },
            height: "100vh",
            borderLeft: 1,
            borderColor: "divider",
            display: "flex",
            flexDirection: "column",
            bgcolor: "background.paper",
          }}
        >
          {/* Existing right panel content... */}
        </Box>
      )}
    </Box>

);
