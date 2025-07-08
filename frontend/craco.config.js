module.exports = {
  devServer: (devServerConfig, { env, paths }) => {
    // Convert webpack-dev-server v4 options to v5 compatible options
    
    // Handle HTTPS option changes
    if (devServerConfig.https !== undefined) {
      if (typeof devServerConfig.https === 'boolean') {
        devServerConfig.server = devServerConfig.https ? 'https' : 'http';
      } else if (typeof devServerConfig.https === 'object') {
        devServerConfig.server = {
          type: 'https',
          options: devServerConfig.https
        };
      }
      delete devServerConfig.https;
    }
    
    // Handle onAfterSetupMiddleware -> setupMiddlewares
    if (devServerConfig.onAfterSetupMiddleware) {
      const oldOnAfterSetupMiddleware = devServerConfig.onAfterSetupMiddleware;
      devServerConfig.setupMiddlewares = (middlewares, devServer) => {
        oldOnAfterSetupMiddleware(devServer);
        return middlewares;
      };
      delete devServerConfig.onAfterSetupMiddleware;
    }

    // Handle onBeforeSetupMiddleware -> setupMiddlewares
    if (devServerConfig.onBeforeSetupMiddleware) {
      const oldOnBeforeSetupMiddleware = devServerConfig.onBeforeSetupMiddleware;
      const oldSetupMiddlewares = devServerConfig.setupMiddlewares;
      devServerConfig.setupMiddlewares = (middlewares, devServer) => {
        oldOnBeforeSetupMiddleware(devServer);
        if (oldSetupMiddlewares) {
          return oldSetupMiddlewares(middlewares, devServer);
        }
        return middlewares;
      };
      delete devServerConfig.onBeforeSetupMiddleware;
    }

    // Handle contentBase -> static
    if (devServerConfig.contentBase) {
      devServerConfig.static = devServerConfig.contentBase;
      delete devServerConfig.contentBase;
    }

    // Handle other deprecated options
    if (devServerConfig.publicPath) {
      if (!devServerConfig.devMiddleware) {
        devServerConfig.devMiddleware = {};
      }
      devServerConfig.devMiddleware.publicPath = devServerConfig.publicPath;
      delete devServerConfig.publicPath;
    }

    return devServerConfig;
  },
};