// This file provides type declarations for the LangFlow custom element
declare namespace JSX {
  interface IntrinsicElements {
    'langflow-chat': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement> & {
      window_title?: string;
      flow_id?: string;
      host_url?: string;
    }, HTMLElement>;
  }
}
