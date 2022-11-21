// This file is replaced with prebuilt bundle in actual extension layer

// Custom handler, runs original handler ensuring Serverless SDK instrumentation

'use strict';

process.env._HANDLER = process.env._ORIGIN_HANDLER;
delete process.env._ORIGIN_HANDLER;

if (!EvalError.$serverlessHandlerFunction && !EvalError.$serverlessHandlerDeferred) {
  const handlerError = EvalError.$serverlessHandlerModuleInitializationError;
  delete EvalError.$serverlessHandlerModuleInitializationError;
  throw handlerError;
}

try {
  const instrument = require('../instrument');

  if (EvalError.$serverlessHandlerDeferred) {
    const handlerDeferred = EvalError.$serverlessHandlerDeferred;
    delete EvalError.$serverlessHandlerDeferred;
    module.exports = handlerDeferred.then((handlerModule) => {
      try {
        if (handlerModule == null) return handlerModule;

        const path = require('path');

        const handlerBasename = path.basename(process.env._HANDLER);
        const handlerModuleBasename = handlerBasename.slice(0, handlerBasename.indexOf('.'));

        const handlerPropertyPathTokens = handlerBasename
          .slice(handlerModuleBasename.length + 1)
          .split('.');
        const handlerFunctionName = handlerPropertyPathTokens.pop();
        let handlerContext = handlerModule;
        while (handlerPropertyPathTokens.length) {
          handlerContext = handlerContext[handlerPropertyPathTokens.shift()];
          if (handlerContext == null) return handlerModule;
        }
        const handlerFunction = handlerContext[handlerFunctionName];
        if (typeof handlerFunction !== 'function') return handlerModule;

        return { handler: instrument(handlerFunction) };
      } catch (error) {
        process._rawDebug(
          'Fatal Serverless SDK Error: ' +
            'Please report at https://github.com/serverless/console/issues: ' +
            'Async handler setup failed'
        );
        throw error;
      }
    });
    return;
  }

  const originalHandler = EvalError.$serverlessHandlerFunction;
  delete EvalError.$serverlessHandlerFunction;

  module.exports.handler = instrument(originalHandler);
} catch (error) {
  process._rawDebug(
    'Fatal Serverless SDK Error: ' +
      'Please report at https://github.com/serverless/console/issues: ' +
      'Handler setup failed'
  );
  throw error;
}
