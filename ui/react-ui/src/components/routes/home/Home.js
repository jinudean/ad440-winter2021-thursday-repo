import React from 'react';
import Container from 'react-bootstrap/esm/Container';
import Alert from 'react-bootstrap/esm/Alert';
import ReactTooltip from 'react-tooltip';
import {withRouter} from "react-router-dom";
import './Home.css';

class Home extends React.Component {
  state = {
    // to add new endpoints, the only thing you need to do is to add your endpoint into this object, 
    // every thing will be done automatically for you. ;)
    endpointsByMethods: {
      GET: [
        {key: '/users', params: []}, 
        {key: '/users/{userId}/tasks', params: [{key: 'userId', value: 0, type: 'number', regex: /{userId}/g}]}
      ]
    },
    badInputAlert: '',
    emptyInputAlert: ''
  };

  handleParamInputChange({method, endpointKey, paramKey, value}) {
    var endpointsByMethods = {...this.state.endpointsByMethods};
    var endpoints = endpointsByMethods[method];
    var endpoint = endpoints.find(endpoint => endpoint.key === endpointKey);
    var param = endpoint.params.find(param => param.key === paramKey);

    // validate user input
    if (value && param.type === 'number' && isNaN(parseInt(value))) {
      this.setState({badInputAlert: "wrong input!! pay attention to the param's type."});

      var input = document.getElementById(paramKey);

      input.value = '';
    }
    else {
      param.value = param.type === 'number' ? parseInt(value) : value;

      this.setState({endpointsByMethods});
    }
  }

  triggerEndpoint({method, endpointKey}) {
    var {history} = this.props;
    var {endpointsByMethods} = this.state;
    var endpoints = endpointsByMethods[method];
    var {params} = endpoints.find(endpoint => endpoint.key === endpointKey);
    var endpoint = endpointKey;
    var updatedEndpoint = endpoint;
    var readyToTrigger = true;

    if (params.length > 0) {
      params.forEach(param => {
        if (param.value) updatedEndpoint = endpoint.replace(param.regex, param.value);
        else {
          readyToTrigger = false;
          this.setState({emptyInputAlert: 'make sure you fill in all required params!!'});
  
          return;
        }
      });
    }

    // push to history to change the endpoint
    if (readyToTrigger) history.push(updatedEndpoint);
  }

  render() {
    var {endpointsByMethods, badInputAlert, emptyInputAlert} = this.state;
    var methods = Object.keys(endpointsByMethods);

    return (
      <Container className="text-center mt-5">
        <h2 className='main-header'>Supported Endpoints:</h2>
        <hr className='main-horizontal-rule'></hr>
        {badInputAlert && <Alert variant="danger" onClose={() => this.setState({badInputAlert: ''})} dismissible>{badInputAlert}</Alert>}
        {emptyInputAlert && <Alert variant="danger" onClose={() => this.setState({emptyInputAlert: ''})} dismissible>{emptyInputAlert}</Alert>}
        {methods.map(method => {
          return (
            <div className='method-container' key={method}>
              <h4 className='method-header'>{method}</h4>
              {endpointsByMethods[method].map(endpoint => {
                return (
                  <div className='endpoints-container' key={endpoint.key}>
                    <ReactTooltip />
                    <div 
                      className='endpoint-title'
                      data-tip='Click to Trigger'  
                      onClick={() => this.triggerEndpoint({method, endpointKey: endpoint.key})}>{endpoint.key}
                    </div>
                    {endpoint.params.map((param, index) => {
                      return (
                        <input 
                          className='param-input' 
                          id={param.key} 
                          type='text' 
                          placeholder={param.key} 
                          key={index}
                          onChange={(event) => this.handleParamInputChange({method, endpointKey: endpoint.key, paramKey: param.key, value: event.target.value})}
                        ></input>
                      )
                    })}
                  </div>
                )
              })}
            </div>
          )
        })}
      </Container>
    )
  }
}

export default withRouter(Home);